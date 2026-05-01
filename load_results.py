#!/usr/bin/env python3

import os
import sys
import csv
from datetime import datetime
from pymongo import MongoClient

def to_int(v):
    try:
        return int(v)
    except:
        return 0

def to_float(v):
    try:
        return float(v)
    except:
        return 0.0

def get_collection():
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("MONGO_DB_NAME", "text_library")
    collection_name = os.environ.get("MONGO_COLLECTION_NAME", "texts")

    if not mongo_uri:
        print("ERROR: MONGO_URI is not set.")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]
    return client, db[collection_name]

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 load_results.py <analysis_output_dir>")
        sys.exit(1)

    analysis_dir = sys.argv[1]
    if not os.path.isdir(analysis_dir):
        print("ERROR: directory does not exist:", analysis_dir)
        sys.exit(1)

    client, collection = get_collection()

    csv_files = [f for f in os.listdir(analysis_dir) if f.endswith("_analysis.csv")]
    if not csv_files:
        print("No analysis csv files found.")
        client.close()
        return

    updated = 0
    skipped = 0

    for fname in csv_files:
        path = os.path.join(analysis_dir, fname)

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if len(rows) == 0:
                skipped += 1
                continue

            row = rows[0]
            source_file = row.get("source_file", "")

            summary = {
                "word_count": to_int(row.get("word_count")),
                "unique_word_count": to_int(row.get("unique_word_count")),
                "character_count": to_int(row.get("character_count")),
                "line_count": to_int(row.get("line_count")),
                "average_word_length": to_float(row.get("average_word_length")),
                "positive_word_count": to_int(row.get("positive_word_count")),
                "negative_word_count": to_int(row.get("negative_word_count")),
                "sentiment_score": to_float(row.get("sentiment_score"))
            }

            result_file_path = row.get("result_file_path", path)

            result = collection.update_one(
                {"file_path": source_file},
                {
                    "$set": {
                        "status": "completed",
                        "result_file_path": result_file_path,
                        "summary_statistics": summary,
                        "loaded_at": datetime.utcnow()
                    }
                }
            )

            if result.matched_count == 0:
                skipped += 1
                print("No matching DB document for source_file:", source_file)
            else:
                updated += 1
                print("Updated:", source_file)

        except Exception as e:
            skipped += 1
            print("Failed to load:", path)
            print(str(e))

    print("Done.")
    print("Updated:", updated)
    print("Skipped:", skipped)

    client.close()

if __name__ == "__main__":
    main()