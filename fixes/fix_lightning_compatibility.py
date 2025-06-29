#!/usr/bin/env python3
"""
Script to modify the training code to work with PyTorch Lightning 2.x
"""

import os
import re
import fileinput
import sys

def fix_pytorch_lightning_imports():
    """Update the PyTorch Lightning imports to be compatible with newer versions."""
    
    # Files to update
    files_to_check = [
        "train_deephase.py",
        "process_dataset.py",
        "train_styleVAE.py",
        "train_transitionNet.py",
        "src/Module/DeepPhase.py"
    ]
    
    # Import patterns to update
    import_replacements = {
        r"from pytorch_lightning\.core\.lightning import LightningModule": "from pytorch_lightning.core.module import LightningModule",
        r"from pytorch_lightning\.callbacks import ModelCheckpoint": "from pytorch_lightning.callbacks import ModelCheckpoint",
        r"from pytorch_lightning\.loggers import TensorBoardLogger": "from pytorch_lightning.loggers import TensorBoardLogger"
    }
    
    # API method and parameter changes
    api_replacements = {
        r"trainer = pl\.Trainer\(gpus=1,": "trainer = pl.Trainer(accelerator='gpu', devices=1,",
        r"trainer = pl\.Trainer\(gpus=\[0\],": "trainer = pl.Trainer(accelerator='gpu', devices=[0],",
        r"\.fit\(model\)": ".fit(model)",
        r"\.test\(model\)": ".test(model)"
    }
    
    # Process each file
    for file_path in files_to_check:
        full_path = os.path.join(os.getcwd(), file_path)
        
        if not os.path.exists(full_path):
            print(f"Skipping {file_path} - file not found")
            continue
            
        print(f"Processing {file_path}")
        
        # Read the file
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Apply replacements
        modified = False
        
        # Update imports
        for pattern, replacement in import_replacements.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                print(f"  - Updated import: {pattern}")
        
        # Update API calls
        for pattern, replacement in api_replacements.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                print(f"  - Updated API call: {pattern}")
        
        # Write back if modified
        if modified:
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"  - Saved changes to {file_path}")
        else:
            print(f"  - No changes needed in {file_path}")

def fix_dataloader_typings():
    """Fix the typings in DataLoader definitions that are causing errors."""
    files_to_check = [
        "src/Datasets/DeepPhaseDataModule.py"
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(os.getcwd(), file_path)
        
        if not os.path.exists(full_path):
            print(f"Skipping {file_path} - file not found")
            continue
            
        print(f"Processing {file_path}")
        
        # Read the file
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Fix List/Union typing issues
        content = content.replace("from typing import List", "from typing import List, Any")
        
        # Remove type annotations that may be causing issues
        modified = False
        
        # Remove problematic typings in DataLoader calls
        dataloader_pattern = r"DataLoader\(([^,]+), batch_size=([^,]+), shuffle=([^,]+), num_workers=([^,]+), drop_last=([^)]+)\)"
        replacement = r"DataLoader(\1, batch_size=\2, shuffle=\3, num_workers=\4, drop_last=\5)"
        
        if re.search(dataloader_pattern, content):
            content = re.sub(dataloader_pattern, replacement, content)
            modified = True
            print(f"  - Fixed DataLoader typings")
        
        # Write back if modified
        if modified:
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"  - Saved changes to {file_path}")
        else:
            print(f"  - No changes needed in {file_path}")

if __name__ == "__main__":
    print("Fixing PyTorch Lightning compatibility issues...")
    fix_pytorch_lightning_imports()
    fix_dataloader_typings()
    print("Done!")
