import os
import sys
from pymongo import MongoClient

def get_collection():
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("MONGO_DB_NAME")
    collection_name = os.environ.get("MONGO_COLLECTION_NAME")

    if not mongo_uri or not db_name or not collection_name:
        print("Missing environment variables.")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db[collection_name]

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 submit_unprocessed.py <output_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "unprocessed_urls.txt")

    collection = get_collection()
    docs = list(collection.find({"status": "unprocessed"}))
    urls = [doc["url"] for doc in docs]

    if not urls:
        print("No unprocessed URLs found.")
        return

    with open(output_file, "w", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")

    print(f"Wrote {len(urls)} URLs to {output_file}")

if __name__ == "__main__":
    main()
