import os
from pymongo import MongoClient

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB_NAME", "text_library")
collection_name = os.environ.get("MONGO_COLLECTION_NAME", "texts")

if not mongo_uri:
    print("ERROR: MONGO_URI is not set.")
    exit(1)

manifest_path = "/scratch/" + os.environ["USER"] + "/group1_texts/manifests/text_files.txt"
os.makedirs(os.path.dirname(manifest_path), exist_ok=True)

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

path_fields = [
    "file_path",
    "local_file_path",
    "downloaded_file_path",
    "text_file_path",
    "source_file_path"
]

records = collection.find({"status": "downloaded"})

lines = []
missing_path_count = 0
missing_file_count = 0

for doc in records:
    file_path = None

    for field in path_fields:
        if field in doc and doc[field]:
            file_path = doc[field]
            break

    if file_path is None:
        missing_path_count = missing_path_count + 1
        print("Skipping record with no file path:", doc.get("_id"))
        continue

    if not os.path.exists(file_path):
        missing_file_count = missing_file_count + 1
        print("Skipping missing file:", file_path)
        continue

    lines.append(str(doc["_id"]) + "\t" + file_path)

with open(manifest_path, "w") as f:
    for line in lines:
        f.write(line + "\n")

print("Manifest created:", manifest_path)
print("Downloaded files ready for Step 4:", len(lines))
print("Downloaded records missing file path:", missing_path_count)
print("Downloaded records with missing local file:", missing_file_count)

if len(lines) == 0:
    print("No downloaded files are ready for Step 4.")
    print("Run Step 3 first so MongoDB records are updated to status='downloaded' with real scratch file paths.")
else:
    print("\nFiles added to manifest:")
    for line in lines:
        print(line)
