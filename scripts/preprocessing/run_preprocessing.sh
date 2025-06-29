#!/bin/bash
# Script to run the preprocessing and save the output to a log file

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting preprocessing at $(date)" > preprocess_log.txt
echo "----------------------------------------" >> preprocess_log.txt

# Run Python script and redirect output to log
python preprocess_complete.py >> preprocess_log.txt 2>&1

echo "----------------------------------------" >> preprocess_log.txt
echo "Finished at $(date)" >> preprocess_log.txt

# Check if output files were created
echo "Checking for output files:" >> preprocess_log.txt
ls -la MotionData/100STYLE/skeleton MotionData/100STYLE/*binary*.dat >> preprocess_log.txt 2>&1

echo "Log file written to: preprocess_log.txt"
