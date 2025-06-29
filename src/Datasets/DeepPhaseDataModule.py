
import numpy as np
import pytorch_lightning as pl
import torch
import torch.utils.data
from torch.utils.data import DataLoader


from src.Datasets.BaseDataSet import StreamDataSetHelper
from src.Datasets.BaseLoader import BasedDataProcessor
from src.Datasets.BatchProcessor import BatchProcessData, BatchProcessDatav2
from src.Datasets.Style100Processor import StyleLoader


class DeepPhaseProcessor(BasedDataProcessor):
    def __init__(self,dt):
        super(DeepPhaseProcessor, self).__init__()
        self.process = BatchProcessData()
        self.dt = dt
    def gpu_fk(self,offsets,hip_pos,local_quat,skeleton):
        quat = torch.from_numpy(local_quat).float().cuda()
        offsets = torch.from_numpy(offsets).float().cuda()
        hip_pos = torch.from_numpy(hip_pos).float().cuda()
        
        # Import our fixed kinematics functions
        try:
            # First try to import the fixed kinematics
            from src.geometry.fixed_kinematics import fixed_forward_kinematics
            
            # Get the parent structure
            if isinstance(skeleton, dict):
                parents = skeleton["parents"]
            else:
                parents = skeleton.parents if hasattr(skeleton, "parents") else [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21]
            
            # Use our fixed version that handles dimension issues
            gp, gq = fixed_forward_kinematics(quat, offsets, hip_pos, parents)
            
        except Exception as e:
            print(f"Error in fixed forward kinematics: {e}")
            print("Attempting fallback methods...")
            
            # Try the original method
            try:
                if hasattr(skeleton, "forward_kinematics"):
                    gp, gq = skeleton.forward_kinematics(quat, offsets, hip_pos)
                else:
                    # Fall back to direct function call
                    from src.geometry import forward_kinematics as fk
                    parents = skeleton["parents"] if isinstance(skeleton, dict) else skeleton.parents
                    gp, gq = fk.forward_kinematics_quats(quat, offsets, hip_pos, parents)
            except Exception as e:
                print(f"Error in forward kinematics fallbacks: {e}")
                # Last resort fallback - hard-coded parents
                from src.geometry import forward_kinematics as fk
                if isinstance(skeleton, dict):
                    parents = skeleton["parents"]
                else:
                    parents = skeleton.parents if hasattr(skeleton, "parents") else [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21]
                
                # Try with manually fixing dimensions
                hip_pos_reshaped = hip_pos.unsqueeze(0).unsqueeze(0) if len(hip_pos.shape) < 3 else hip_pos
                gp, gq = fk.forward_kinematics_quats(quat, offsets, hip_pos_reshaped, parents)
            
        return gp, gq[...,0:1,:]
    def transform_single(self,offsets,hip_pos,local_quat,skeleton):
        gp,gq = self.gpu_fk(offsets,hip_pos,local_quat,skeleton)
        dict = self.process(gq.unsqueeze(0),gp.unsqueeze(0))
        lp = dict['local_pos'][0]
        relative_gv = (lp[:,1:]-lp[:,:-1])/self.dt
        torch.cuda.empty_cache()

        return relative_gv

    #((V_i in R_i) - (V_(i - 1) in R_(i - 1))) / dt,
    def __call__(self, dict,skeleton,motionDataLoader):
        offsets, hip_pos, quats = dict["offsets"], dict["hip_pos"], dict["quats"]
        dict = {"gv":[]}
        if(len(offsets)>1):
            offsets = np.concatenate(offsets,axis=0)
            hip_pos = np.concatenate(hip_pos,axis=0)
            quats = np.concatenate(quats,axis=0)
        else:
            offsets = offsets[0][np.newaxis,...]
            hip_pos = hip_pos[0][np.newaxis,...]
            quats = quats[0][np.newaxis,...]
        gv = self.transform_single(offsets, hip_pos,quats, skeleton)
        gv = gv.cpu().numpy()
        dict['gv']=gv

        return dict



class DeepPhaseProcessorv2(BasedDataProcessor):
    def __init__(self,dt):
        super(DeepPhaseProcessorv2, self).__init__()
        self.process = BatchProcessDatav2()
        self.dt = dt
    def gpu_fk(self,offsets,hip_pos,local_quat,skeleton):
        quat = torch.from_numpy(local_quat).float().cuda()
        offsets = torch.from_numpy(offsets).float().cuda()
        hip_pos = torch.from_numpy(hip_pos).float().cuda()
        
        # Handle different skeleton types
        if hasattr(skeleton, "forward_kinematics"):
            gp,gq = skeleton.forward_kinematics(quat,offsets,hip_pos)
        else:
            # Fall back to direct function call
            from src.geometry import forward_kinematics as fk
            parents = skeleton["parents"] if isinstance(skeleton, dict) else skeleton.parents
            gp,gq = fk.forward_kinematics_quats(quat,offsets,hip_pos,parents)

        return gp,gq[...,0:1,:]
    def transform_single(self,offsets,hip_pos,local_quat,skeleton):
        gp,gq = self.gpu_fk(offsets,hip_pos,local_quat,skeleton)
        glb_vel,glb_pos,glb_rot,root_rotatioin = self.process.forward(gq.unsqueeze(0),gp.unsqueeze(0))
        relative_gv = glb_vel[0]/self.dt
        torch.cuda.empty_cache()
        return relative_gv

    #((V_i in R_i) - (V_(i - 1) in R_(i - 1))) / dt,
    def __call__(self, dict,skeleton,motionDataLoader):
        offsets, hip_pos, quats = dict["offsets"], dict["hip_pos"], dict["quats"]
        dict = {"gv":[]}
        all_std = 0
        length = 0
        for i in range(len(offsets)):
            N,J,D = quats[i].shape
            dict["gv"].append(self.transform_single(offsets[i],hip_pos[i],quats[i],skeleton))
            all_std = all_std + dict['gv'][-1].std() * dict['gv'][-1].shape[0]
            length = length + dict['gv'][-1].shape[0]
        all_std = all_std/length
        dict['std'] = all_std
        return dict
class DeephaseDatasetWindow(torch.utils.data.Dataset):
    def __init__(self,buffer):
        self.buffer = buffer
    def __getitem__(self, item):
        return self.buffer[item]
    def __len__(self):
        return self.buffer.shape[0]
class DeephaseDataSet(torch.utils.data.Dataset):
    def __init__(self,buffer,window_size):
        self.window = window_size
        # first remove sequence less than window
        idx = [i for i in range(len(buffer)) if buffer[i].shape[0]>=window_size]
        buffer = [buffer[i] for i in idx]

        self.streamer = StreamDataSetHelper(buffer,window_size)
        self.buffer = buffer


    def get_window(self,item):
        idx, frame_idx = self.streamer[item]
        return idx,[frame_idx,frame_idx+self.window]
    def __getitem__(self, item):
        idx,frame_idx = self.streamer[item]
        return self.buffer[idx][frame_idx:frame_idx+self.window]
    def __len__(self):
        return len(self.streamer)
class Style100DataModule(pl.LightningDataModule):
    def __init__(self,batch_size,shuffle,data_loader:StyleLoader,window_size):
        super(Style100DataModule, self).__init__()
        self.batch_size = batch_size
        self.shuffle = shuffle

        self.data_loader = data_loader

        data_loader.load_skeleton_only()
        self.skeleton = data_loader.skeleton
        self.window = window_size
    def setup(self,stage: [str] = None) :
        use_gv=True
        if(use_gv):
            self.data_loader.load_train_test_dataset("deep_phase_gv")
            self.test_set = DeephaseDatasetWindow(self.data_loader.test_dict['gv'])
            self.train_set = DeephaseDatasetWindow(self.data_loader.train_dict['gv'])
            self.scale = 1.
        else:
            self.data_loader.load_train_test_dataset("deep_phase_pca")
            self.test_set = DeephaseDataSet(self.data_loader.test_dict['pos'], self.window)
            self.train_set = DeephaseDataSet(self.data_loader.train_dict['pos'], self.window)
            self.scale = 1.


        self.val_set = self.test_set


    def train_dataloader(self):
        return DataLoader(self.train_set, batch_size=self.batch_size, shuffle=self.shuffle, num_workers=0, drop_last=True)

    def val_dataloader(self):  # 需要shuffle确保相同batch内的风格不相同
        return DataLoader(self.val_set, batch_size=self.batch_size, shuffle=False, num_workers=0, drop_last=True)

    def test_dataloader(self):
        return DataLoader(self.test_set, batch_size=self.batch_size, shuffle=False, num_workers=16, drop_last=True)
    def on_after_batch_transfer(self, batch, dataloader_idx: int) :
        self.scale= 1.
        return on_after_batch_transfer(batch,self.scale)




def on_after_batch_transfer(batch,scale):
    use_gv = True
    if (use_gv):
        batch = batch.permute(0, 2, 3, 1).contiguous()
        B, J, D, N = batch.shape
        batch = batch/30.
        mean = torch.mean(batch, dim=(-1), keepdim=True)
        batch = batch - mean

    batch = batch.to(torch.float)
    return batch
