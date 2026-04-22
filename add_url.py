import os
import sys
from datetime import datetime
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
        print("Usage: python3 add_url.py <text_url>")
        sys.exit(1)

    url = sys.argv[1].strip()
    collection = get_collection()

    existing = collection.find_one({"url": url})
    if existing:
        print("URL already exists.")
        return

    doc = {
        "url": url,
        "status": "unprocessed",
        "added_at": datetime.utcnow().isoformat()
    }

    collection.insert_one(doc)
    print("Inserted URL successfully!")

if __name__ == "__main__":
    main()
