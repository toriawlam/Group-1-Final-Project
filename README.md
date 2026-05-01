# DS 2002 Final Project — Text Analyzer (Project B)

**Team:** Compute Collective — Dannon, Shlok, Emma, Victoria, Kriti

We scrape plain-text book URLs into MongoDB, download files on UVA HPC scratch, analyze them with a Slurm job array, and check results with a query script.

## What you need

- Python 3
- Packages in `requirements.txt` (`pip install -r requirements.txt`)
- MongoDB Atlas

## Environment variables

```bash
export MONGO_URI="your-atlas-connection-string"
export MONGO_DB_NAME="text_library"
export MONGO_COLLECTION_NAME="texts"
```

## Directories on HPC (recommended)

These paths match what the scripts expect under `/scratch/$USER/group1_texts/`. Run once on the HPC login node before the pipeline:

```bash
export BASE_DIR="/scratch/$USER/group1_texts"
export INPUT_DIR="$BASE_DIR/input"
export OUTPUT_DIR="$BASE_DIR/output"
export MANIFEST_DIR="$BASE_DIR/manifests"
export LOG_DIR="$BASE_DIR/logs"

mkdir -p "$INPUT_DIR" "$OUTPUT_DIR" "$MANIFEST_DIR" "$LOG_DIR"
```

## Scripts (run in this order)

Export the Mongo env vars **and** the directory vars above (`BASE_DIR`, `INPUT_DIR`, `OUTPUT_DIR`, `MANIFEST_DIR`, `LOG_DIR`) in the same shell session before these commands.

1. **`add_url.py`** — Adds URL if missing, status `unprocessed`.

   ```bash
   python3 add_url.py "<url>"
   ```

2. **`submit_unprocessed.py`** — Writes `unprocessed_urls.txt` under `$BASE_DIR`.

   ```bash
   python3 submit_unprocessed.py "$BASE_DIR"
   ```

3. **`download_unprocessed.py`** — Saves files under `$INPUT_DIR`; sets status `downloaded`.

   ```bash
   python3 download_unprocessed.py
   ```

4. **`make_manifest.py`** — Builds `$MANIFEST_DIR/text_files.txt` (Mongo `_id` and path).

   ```bash
   python3 make_manifest.py
   ```

5. **`slurm_text_array.sh`** — Submit a job array sized to the manifest. Each task runs `analyze_text_file.py`, which writes `*_analysis.csv` under `$OUTPUT_DIR`.

   ```bash
   M="$MANIFEST_DIR/text_files.txt"
   N=$(wc -l < "$M")
   sbatch --array=0-$((N-1)) slurm_text_array.sh "$M" "$OUTPUT_DIR"
   ```

6. **`load_results.py`** — Read analysis CSV files in `$OUTPUT_DIR` and merge final metrics/status into MongoDB.

   ```bash
   python3 load_results.py "$OUTPUT_DIR"
   ```

7. **`query_results.py`** — Print pipeline status counts and record details.

   ```bash
   python3 query_results.py
   ```
