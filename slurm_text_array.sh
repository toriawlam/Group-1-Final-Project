#!/bin/bash
#SBATCH --job-name=text-array
#SBATCH --partition=standard
#SBATCH --output=slurm-%A_%a.out
#SBATCH --error=slurm-%A_%a.err
#SBATCH --time=00:05:00
#SBATCH --mem=1G

URL_FILE=$1
OUTPUT_DIR=$2

echo "Running task $SLURM_ARRAY_TASK_ID"
echo "URL file: $URL_FILE"
echo "Output dir: $OUTPUT_DIR"

URL=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$URL_FILE")
echo "Assigned URL: $URL"
