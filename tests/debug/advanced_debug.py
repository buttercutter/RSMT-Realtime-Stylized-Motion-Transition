import os
import sys
import traceback

# Redirect stdout to a file to capture all output
stdout_backup = sys.stdout
sys.stdout = open('debug_output.log', 'w')

try:
    print("=== Environment ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"PATH: {os.environ.get('PATH')}")
    
    print("\n=== File Structure ===")
    style_dir = "./MotionData/100STYLE/"
    print(f"100STYLE directory exists: {os.path.exists(style_dir)}")
    
    if os.path.exists(style_dir):
        print(f"Contents of {style_dir}:")
        for item in os.listdir(style_dir):
            print(f"  - {item}")
    
    print("\n=== Libraries ===")
    try:
        import numpy
        print(f"NumPy version: {numpy.__version__}")
    except ImportError:
        print("NumPy is not installed")
    except Exception as e:
        print(f"Error checking NumPy: {str(e)}")
    
    try:
        import pandas
        print(f"Pandas version: {pandas.__version__}")
    except ImportError:
        print("Pandas is not installed")
    except Exception as e:
        print(f"Error checking Pandas: {str(e)}")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("PyTorch is not installed")
    except Exception as e:
        print(f"Error checking PyTorch: {str(e)}")
    
    print("\n=== Module Import Test ===")
    sys.path.insert(0, os.path.abspath('.'))
    
    try:
        print("Trying to import src.Datasets.Style100Processor...")
        from src.Datasets import Style100Processor
        print("✓ Successfully imported Style100Processor module")
        
        print("Checking bvh_to_binary function...")
        if hasattr(Style100Processor, 'bvh_to_binary'):
            print("✓ bvh_to_binary function exists")
        else:
            print("✗ bvh_to_binary function does not exist")
            print("Available attributes in Style100Processor:")
            for attr in dir(Style100Processor):
                if not attr.startswith('__'):
                    print(f"  - {attr}")
    except Exception as e:
        print(f"✗ Error importing Style100Processor: {str(e)}")
        traceback.print_exc()
    
    try:
        print("\nTrying to import src.utils.BVH_mod...")
        from src.utils import BVH_mod
        print("✓ Successfully imported BVH_mod")
    except Exception as e:
        print(f"✗ Error importing BVH_mod: {str(e)}")
        traceback.print_exc()
    
    print("\n=== Frame_Cuts.csv Check ===")
    try:
        import pandas as pd
        frame_cuts_path = os.path.join(style_dir, "Frame_Cuts.csv")
        if os.path.exists(frame_cuts_path):
            frame_cuts = pd.read_csv(frame_cuts_path)
            print(f"Successfully loaded Frame_Cuts.csv")
            print(f"Number of rows: {len(frame_cuts)}")
            print(f"Columns: {', '.join(frame_cuts.columns)}")
            print(f"First 3 rows:")
            print(frame_cuts.head(3))
        else:
            print(f"Frame_Cuts.csv not found at {frame_cuts_path}")
    except Exception as e:
        print(f"Error reading Frame_Cuts.csv: {str(e)}")
        traceback.print_exc()
    
    print("\n=== BVH File Check ===")
    try:
        sample_style = "Aeroplane"
        sample_content = "BR"
        sample_bvh_path = os.path.join(style_dir, sample_style, f"{sample_style}_{sample_content}.bvh")
        
        if os.path.exists(sample_bvh_path):
            print(f"BVH file exists: {sample_bvh_path}")
            print(f"File size: {os.path.getsize(sample_bvh_path)} bytes")
            
            # Read first few lines of the BVH file
            with open(sample_bvh_path, 'r') as f:
                print("First 10 lines of the BVH file:")
                for i, line in enumerate(f):
                    if i < 10:
                        print(f"  {line.strip()}")
                    else:
                        break
        else:
            print(f"BVH file not found: {sample_bvh_path}")
            
            # Check the style directory
            style_path = os.path.join(style_dir, sample_style)
            if os.path.exists(style_path):
                print(f"Style directory exists: {style_path}")
                print(f"Files in {style_path}:")
                for file in os.listdir(style_path):
                    print(f"  - {file}")
            else:
                print(f"Style directory not found: {style_path}")
    except Exception as e:
        print(f"Error checking BVH file: {str(e)}")
        traceback.print_exc()

except Exception as e:
    print(f"Critical error: {str(e)}")
    traceback.print_exc()

finally:
    # Restore stdout
    sys.stdout.close()
    sys.stdout = stdout_backup
    
    # Print the path to the log file
    print(f"Debug information has been written to {os.path.abspath('debug_output.log')}")
    print("Please check this file for detailed diagnostic information.")
