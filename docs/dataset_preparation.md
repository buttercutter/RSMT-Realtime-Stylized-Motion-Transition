# Dataset Preparation

This guide explains how to prepare the 100STYLE dataset for training the RSMT model. The preparation process involves downloading the dataset, converting BVH files to binary format, and creating the necessary data structures.

## Downloading the 100STYLE Dataset

1. Download the 100STYLE dataset from [https://www.ianxmason.com/100style/](https://www.ianxmason.com/100style/)
2. Extract the downloaded files and place them in the `MotionData/100STYLE/` directory

The dataset should include various style folders, each containing different motion content files in BVH format.

## Dataset Structure

The 100STYLE dataset contains motion captures from various styles, with each style having multiple motion contents:

- Style categories (folders): Aeroplane, Angry, Anxious, Bow, etc.
- Motion contents (files): Each style folder contains files like `StyleName_BR.bvh`, `StyleName_BW.bvh`, etc.
  - BR: Basic Run
  - BW: Basic Walk
  - FR: Fast Run
  - FW: Fast Walk
  - ID: Idle
  - SR: Slow Run
  - SW: Slow Walk
  - TR1, TR2, TR3: Turn variants

## Preprocessing Methods

There are multiple ways to preprocess the dataset:

### Option 1: Using the Built-in Script

This is the simplest method, using the provided script:

```bash
python process_dataset.py --preprocess
```

This command:
1. Converts all BVH files to binary format
2. Creates a skeleton file capturing the joint hierarchy
3. Splits the data into training and testing sets
4. Augments the dataset with mirrored versions

### Option 2: Using `preprocess_complete.py`

For more control over the preprocessing steps, you can use the comprehensive preprocessing script:

```bash
python preprocess_complete.py
```

This script provides detailed progress information and has additional error-handling capabilities.

### Option 3: Manual Step-by-Step Preprocessing

If you need to customize the preprocessing or troubleshoot issues:

1. Convert BVH files to binary:
   ```bash
   python -c "from src.Datasets.Style100Processor import bvh_to_binary; bvh_to_binary()"
   ```

2. Create the skeleton file:
   ```bash
   python -c "from src.Datasets.Style100Processor import save_skeleton; save_skeleton()"
   ```

3. Split into train and test datasets:
   ```bash
   python -c "import process_dataset; process_dataset.splitStyle100TrainTestSet()"
   ```

## Expected Outputs

After successful preprocessing, your `MotionData/100STYLE/` directory should contain:

- `skeleton`: The skeleton structure file
- `test_binary.dat`: Test dataset in binary format
- `train_binary.dat`: Training dataset in binary format
- `test_binary_agument.dat`: Augmented test dataset
- `train_binary_agument.dat`: Augmented training dataset

## Frame Cuts

The 100STYLE dataset includes a `Frame_Cuts.csv` file that specifies the start and end frames for each motion segment. The preprocessing scripts use this information to properly segment the motions.

## Troubleshooting

If you encounter issues during preprocessing:

1. Ensure the dataset is correctly placed in the `MotionData/100STYLE/` directory
2. Verify that the `Frame_Cuts.csv` file exists and is correctly formatted
3. Check that the required dependencies are installed
4. If using a GPU for accelerated processing, verify CUDA is properly installed

For more detailed troubleshooting, refer to the [Troubleshooting](troubleshooting.md) guide.

## Next Steps

After successful preprocessing, follow the [Training Pipeline](training_pipeline.md) guide to train the RSMT model.
