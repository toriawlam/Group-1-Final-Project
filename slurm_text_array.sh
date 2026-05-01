#!/bin/bash
#SBATCH --job-name=text-array
#SBATCH --partition=standard
#SBATCH --output=/scratch/%u/group1_texts/logs/slurm-%A_%a.out
#SBATCH --error=/scratch/%u/group1_texts/logs/slurm-%A_%a.err
#SBATCH --time=00:05:00
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1

module load miniforge

MANIFEST_FILE=$1
OUTPUT_DIR=$2

echo "Running task $SLURM_ARRAY_TASK_ID"
echo "Manifest file: $MANIFEST_FILE"
echo "Output dir: $OUTPUT_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$MANIFEST_FILE")

DOC_ID=$(echo "$LINE" | cut -f1)
TEXT_FILE=$(echo "$LINE" | cut -f2-)

echo "Document ID: $DOC_ID"
echo "Assigned text file: $TEXT_FILE"

python3 analyze_text_file.py "$DOC_ID" "$TEXT_FILE" "$OUTPUT_DIR"
