import os
import re
import sys
import requests
from datetime import datetime
from pymongo import MongoClient

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB_NAME", "text_library")
collection_name = os.environ.get("MONGO_COLLECTION_NAME", "texts")

if not mongo_uri:
    print("ERROR: MONGO_URI is not set.")
    sys.exit(1)

input_dir = "/scratch/" + os.environ["USER"] + "/group1_texts/input"
os.makedirs(input_dir, exist_ok=True)

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

docs = list(collection.find({"status": "unprocessed"}))

if not docs:
    print("No unprocessed records found.")
    sys.exit(0)

for doc in docs:
    url = doc.get("url")

    if not url:
        print("Skipping record with no URL:", doc.get("_id"))
        continue

    print("Downloading:", url)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        url_part = url.rstrip("/").split("/")[-1]
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", url_part)

        if not safe_name.endswith(".txt"):
            safe_name = safe_name + ".txt"

        file_path = os.path.join(input_dir, safe_name)

        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(response.text)

        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "status": "downloaded",
                    "file_path": file_path,
                    "downloaded_at": datetime.utcnow()
                }
            }
        )

        print("Saved to:", file_path)

    except Exception as e:
        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "status": "error",
                    "error_message": str(e),
                    "downloaded_at": datetime.utcnow()
                }
            }
        )

        print("ERROR downloading:", url)
        print(e)
