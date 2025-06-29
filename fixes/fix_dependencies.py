#!/usr/bin/env python3
"""
Script to update dependencies and fix compatibility issues
"""

import os
import sys
import subprocess
import pkg_resources

def print_section(title):
    print(f"\n{'-' * 60}")
    print(f" {title}")
    print(f"{'-' * 60}")

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("Success!")
        if result.stdout.strip():
            print(result.stdout.strip())
    else:
        print(f"Error (code {result.returncode}):")
        print(result.stderr.strip())
    return result.returncode == 0

def main():
    print_section("RSMT Dependency Fixer")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    print(f"Using virtual environment: {in_venv}")
    if not in_venv:
        print("WARNING: Not running in a virtual environment. It's recommended to use one.")
        response = input("Do you want to create a virtual environment? (y/n): ")
        if response.lower() == 'y':
            run_command("python -m venv .venv")
            print("Virtual environment created at .venv")
            print("Please activate the environment and run this script again:")
            print("  source .venv/bin/activate  # On Linux/Mac")
            print("  .venv\\Scripts\\activate  # On Windows")
            return
    
    # Upgrade pip
    print_section("Upgrading pip")
    run_command("pip install --upgrade pip")
    
    # Install/upgrade basic dependencies
    print_section("Installing basic dependencies")
    base_deps = [
        "numpy>=1.22.3",
        "pandas>=1.4.3",
        "matplotlib>=3.5.2",
        "scipy>=1.9.0"
    ]
    for dep in base_deps:
        run_command(f"pip install {dep}")
    
    # Install PyTorch with CUDA support
    print_section("Installing PyTorch")
    torch_command = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    run_command(torch_command)
    
    # Verify PyTorch installation and CUDA availability
    print_section("Verifying PyTorch and CUDA")
    verify_torch = """
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU device count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)"
"""
    run_command(verify_torch)
    
    # Install PyTorch3D (this can be tricky)
    print_section("Installing PyTorch3D")
    print("Attempting multiple methods to install PyTorch3D...")
    
    # Method 1: Install from PyPI (might work with newer PyTorch versions)
    success = run_command("pip install pytorch3d")
    
    # Method 2: If Method 1 fails, try installing from conda-forge
    if not success:
        print("PyPI installation failed, trying with conda-forge...")
        success = run_command("conda install -c conda-forge pytorch3d -y") if run_command("which conda") else False
    
    # Method 3: If Methods 1 and 2 fail, try installing from source
    if not success:
        print("Conda installation not available or failed, trying to install from source...")
        success = run_command("pip install --no-build-isolation 'git+https://github.com/facebookresearch/pytorch3d.git@stable'")
    
    # Method 4: Create a simple compatibility layer if all else fails
    if not success:
        print("All installation methods failed. Creating a compatibility layer...")
        create_pytorch3d_compat()
        success = True
    
    # Install PyTorch Lightning
    print_section("Installing PyTorch Lightning")
    run_command("pip install pytorch-lightning>=1.5.10")
    
    # Check if patches are needed for code compatibility
    print_section("Checking for code compatibility")
    check_code_compatibility()
    
    print_section("Dependency Setup Complete")
    print("\nYou should now be able to run the RSMT code. If you still encounter issues,")
    print("check the troubleshooting guide in docs/troubleshooting.md")

def create_pytorch3d_compat():
    """Create a minimal compatibility layer for PyTorch3D if it can't be installed."""
    code = """# Compatibility layer for PyTorch3D transforms
import torch

def quaternion_apply(quaternion, point):
    \"\"\"
    Apply the rotation given by a quaternion to a point.
    \"\"\"
    q = torch.unsqueeze(quaternion, -2)  # (..., 1, 4)
    
    # Extract quaternion components
    q_real = q[..., 0]
    q_imag = q[..., 1:]
    
    # Point is in vector form, so only has 3 components
    # Compute the quaternion-point-quaternion_conjugate product
    # First, compute the vector by which to rotate the point
    real_vec_cross = torch.cross(q_imag, point, dim=-1)
    real_vec = point * q_real.unsqueeze(-1)
    vector = 2.0 * real_vec_cross + point + 2.0 * torch.cross(q_imag, real_vec_cross, dim=-1)
    return vector

def quaternion_multiply(q1, q2):
    \"\"\"
    Multiply quaternions q1 and q2.
    \"\"\"
    # Extract components
    w1, x1, y1, z1 = q1[..., 0], q1[..., 1], q1[..., 2], q1[..., 3]
    w2, x2, y2, z2 = q2[..., 0], q2[..., 1], q2[..., 2], q2[..., 3]
    
    # Compute the quaternion product
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    
    # Stack the components
    quat = torch.stack([w, x, y, z], dim=-1)
    return quat
"""
    # Save the compatibility module
    compat_dir = "src/geometry/pytorch3d_transforms.py"
    with open(compat_dir, "w") as f:
        f.write(code)
    print(f"Created compatibility layer at {compat_dir}")
    
    # Create __init__.py if it doesn't exist
    init_path = "src/geometry/__init__.py"
    if not os.path.exists(init_path):
        with open(init_path, "a") as f:
            pass  # Create empty file
    
    # Add import to BVH_mod.py to use our compatibility layer instead
    patches = [
        {
            'file': 'src/utils/BVH_mod.py',
            'find': 'import pytorch3d.transforms as trans',
            'replace': '# Using custom compatibility layer instead of pytorch3d\nimport src.geometry.pytorch3d_transforms as trans'
        }
    ]
    
    for patch in patches:
        apply_patch(patch['file'], patch['find'], patch['replace'])

def check_code_compatibility():
    """Check for and apply patches to ensure code compatibility with modern dependencies."""
    # Update DeepPhaseDataModule.py to handle different skeleton types
    patches = [
        {
            'file': 'src/Datasets/DeepPhaseDataModule.py',
            'find': '    def gpu_fk(self,offsets,hip_pos,local_quat,skeleton):\n        quat = torch.from_numpy(local_quat).float().cuda()\n        offsets = torch.from_numpy(offsets).float().cuda()\n        hip_pos = torch.from_numpy(hip_pos).float().cuda()\n        gp,gq = skeleton.forward_kinematics(quat,offsets,hip_pos)',
            'replace': '    def gpu_fk(self,offsets,hip_pos,local_quat,skeleton):\n        quat = torch.from_numpy(local_quat).float().cuda()\n        offsets = torch.from_numpy(offsets).float().cuda()\n        hip_pos = torch.from_numpy(hip_pos).float().cuda()\n        \n        # Handle different skeleton types\n        if hasattr(skeleton, "forward_kinematics"):\n            gp,gq = skeleton.forward_kinematics(quat,offsets,hip_pos)\n        else:\n            # Fall back to direct function call\n            from src.geometry import forward_kinematics as fk\n            parents = skeleton["parents"] if isinstance(skeleton, dict) else skeleton.parents\n            gp,gq = fk.forward_kinematics_quats(quat,offsets,hip_pos,parents)'
        }
    ]
    
    for patch in patches:
        apply_patch(patch['file'], patch['find'], patch['replace'])

def apply_patch(file_path, find_text, replace_text):
    """Apply a patch to a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if find_text not in content:
            print(f"Patch for {file_path} not needed or couldn't find pattern.")
            return False
            
        new_content = content.replace(find_text, replace_text)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
            
        print(f"Successfully patched {file_path}")
        return True
    except Exception as e:
        print(f"Error applying patch to {file_path}: {e}")
        return False

if __name__ == "__main__":
    main()
