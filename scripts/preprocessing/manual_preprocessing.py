import os
import pickle
import numpy as np
import pandas as pd
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.abspath('.'))

def swap_joints(quats, offsets, parents, names):
    """Swap joint ordering to match the target skeleton"""
    order = ["Hips",
             "LeftHip","LeftKnee","LeftAnkle","LeftToe",
             "RightHip","RightKnee","RightAnkle","RightToe",
             "Chest","Chest2","Chest3","Chest4","Neck","Head",
             "LeftCollar","LeftShoulder","LeftElbow","LeftWrist",
             "RightCollar","RightShoulder","RightElbow","RightWrist"]
    
    ori_order = {name:i for i,name in enumerate(names)}
    n_quats = np.empty_like(quats)
    n_offsets = np.empty_like(offsets)
    n_parents = parents.copy()
    
    for i, name in enumerate(order):
        or_idx = ori_order[name]
        n_quats[:, i] = quats[:, or_idx]
        n_offsets[i] = offsets[or_idx]
    
    return n_quats, n_offsets, n_parents, order

def read_bvh_file(file_path):
    """Simple BVH reader function - replace the full implementation for now"""
    from src.utils.BVH_mod import read_bvh
    try:
        anim = read_bvh(file_path)
        return anim
    except Exception as e:
        print(f"Error reading BVH file {file_path}: {str(e)}")
        return None

def subsample_motion(anim, ratio=2):
    """Subsample a motion sequence"""
    if hasattr(anim, 'quats') and hasattr(anim, 'hip_pos'):
        # Take every nth frame
        anim.quats = anim.quats[::ratio]
        anim.hip_pos = anim.hip_pos[::ratio]
    return anim

def manual_bvh_to_binary():
    """Convert BVH files to binary without using pytorch3d"""
    print("Starting manual BVH to binary conversion...")
    
    root_dir = "./MotionData/100STYLE/"
    frame_cuts = pd.read_csv(root_dir + "Frame_Cuts.csv")
    n_styles = len(frame_cuts.STYLE_NAME)
    style_name = [frame_cuts.STYLE_NAME[i] for i in range(n_styles)]
    content_name = ["BR", "BW", "FR", "FW", "ID", "SR", "SW", "TR1", "TR2", "TR3"]

    def extractSeqRange(start, end):
        start = start.astype('Int64')
        end = end.astype('Int64')
        return [[(start[i]),(end[i])] for i in range(len(start))]
    
    content_range = {name:extractSeqRange(frame_cuts[name+"_START"],frame_cuts[name+"_STOP"]) for name in content_name}
    
    def clip_anim(anim, start, end):
        if anim and hasattr(anim, 'quats') and hasattr(anim, 'hip_pos'):
            anim.quats = anim.quats[start:end]
            anim.hip_pos = anim.hip_pos[start:end]
        return anim
    
    # Process each style
    for i in range(n_styles):
        print(f"Processing style {i+1}/{n_styles}: {style_name[i]}")
        anim_style = {}
        folder = root_dir + style_name[i] + "/"
        
        for content in content_name:
            ran = content_range[content][i]
            if isinstance(ran[0], int):  # Check if it's a valid range
                file = folder + style_name[i] + "_" + content + ".bvh"
                
                if os.path.exists(file):
                    try:
                        from src.utils.BVH_mod import read_bvh
                        from src.Datasets.Style100Processor import Swap100StyJoints
                        
                        # Use the original function if it works
                        anim = read_bvh(file, remove_joints=Swap100StyJoints())
                        anim = clip_anim(anim, ran[0], ran[1])
                        anim = subsample_motion(anim, 2)
                        
                        if anim and hasattr(anim, 'quats'):
                            anim_style[content] = {
                                "quats": anim.quats.astype(np.float32),
                                "offsets": anim.offsets.astype(np.float32),
                                "hips": anim.hip_pos.astype(np.float32)
                            }
                            print(f"  Processed {content}")
                        else:
                            print(f"  Failed to process {content}: Invalid animation data")
                    except Exception as e:
                        print(f"  Error processing {file}: {str(e)}")
                else:
                    print(f"  File not found: {file}")
        
        # Save the binary file for this style
        binary_path = folder + "binary.dat"
        try:
            with open(binary_path, "wb") as f:
                pickle.dump(anim_style, f)
            print(f"  Saved {binary_path}")
        except Exception as e:
            print(f"  Error saving {binary_path}: {str(e)}")
    
    print("BVH to binary conversion complete!")

def manual_save_skeleton():
    """Save the skeleton structure without using pytorch3d"""
    print("Saving skeleton...")
    
    root_dir = "./MotionData/100STYLE/"
    try:
        from src.utils.BVH_mod import read_bvh
        from src.Datasets.Style100Processor import Swap100StyJoints
        
        anim = read_bvh(root_dir + "Aeroplane/Aeroplane_BR.bvh", remove_joints=Swap100StyJoints())
        with open(root_dir + "skeleton", "wb") as f:
            pickle.dump(anim.skeleton, f)
        print("Skeleton saved successfully!")
    except Exception as e:
        print(f"Error saving skeleton: {str(e)}")

def manual_split_dataset():
    """Split the dataset into train and test sets"""
    print("Splitting dataset into train and test sets...")
    
    folder = "./MotionData/100STYLE/"
    
    try:
        # Read the motion data from binary files
        frame_cuts = pd.read_csv(folder + "Frame_Cuts.csv")
        n_styles = len(frame_cuts.STYLE_NAME)
        style_names = [frame_cuts.STYLE_NAME[i] for i in range(n_styles)]
        
        # Load all motion data
        all_motions = {}
        for i, style in enumerate(style_names):
            style_folder = folder + style + "/"
            binary_path = style_folder + "binary.dat"
            
            if os.path.exists(binary_path):
                with open(binary_path, "rb") as f:
                    motion_data = pickle.load(f)
                all_motions[style] = motion_data
            else:
                print(f"Binary file not found for {style}")
        
        # Split into train and test
        train_motions = {}
        test_motions = {}
        
        for style in style_names[:-10]:  # Last 10 styles are for testing
            train_motions[style] = {}
            test_motions[style] = {}
            
            for content in all_motions[style].keys():
                seq = all_motions[style][content]
                length = seq['quats'].shape[0]
                
                if length > 2000:
                    test_length = length // 10
                    
                    train_motions[style][content] = {}
                    train_motions[style][content]['quats'] = seq['quats'][:-test_length]
                    train_motions[style][content]['offsets'] = seq['offsets']
                    train_motions[style][content]['hips'] = seq['hips'][:-test_length]
                    
                    test_motions[style][content] = {}
                    test_motions[style][content]['quats'] = seq['quats'][-test_length:]
                    test_motions[style][content]['offsets'] = seq['offsets']
                    test_motions[style][content]['hips'] = seq['hips'][-test_length:]
                else:
                    train_motions[style][content] = seq
        
        # Last 10 styles go directly to test
        for style in style_names[-10:]:
            test_motions[style] = all_motions[style]
        
        # Save train and test sets
        with open(folder + "train_binary.dat", "wb") as f:
            pickle.dump(train_motions, f)
        print(f"Train set saved: {len(train_motions)} styles")
        
        with open(folder + "test_binary.dat", "wb") as f:
            pickle.dump(test_motions, f)
        print(f"Test set saved: {len(test_motions)} styles")
        
        print("Dataset splitting complete!")
    except Exception as e:
        print(f"Error splitting dataset: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Run all preprocessing steps"""
    try:
        manual_bvh_to_binary()
        manual_save_skeleton()
        manual_split_dataset()
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
