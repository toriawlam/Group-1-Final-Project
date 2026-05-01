#!/usr/bin/env python3

from pymongo import MongoClient
import sys
import os
import logging
import datetime

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB_NAME", "text_library")
collection_name = os.environ.get("MONGO_COLLECTION_NAME", "texts")

def parse_args():
    try:
        url = sys.argv[1]
    except IndexError:
        logging.error("Usage: python3 " + sys.argv[0] + " <url>")
        sys.exit(1)

    return url

def check_url(this_url):
    if not mongo_uri:
        print("ERROR: MONGO_URI is not set.")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    if collection.find_one({"url": this_url}):
        print("This URL already exists in the text library.")
    else:
        collection.insert_one({
            "url": this_url,
            "status": "unprocessed",
            "added_at": datetime.datetime.utcnow()
        })
        print("This URL has been added to the text library.")

    client.close()

def main():
    this_url = parse_args()
    check_url(this_url)

if __name__ == "__main__":
    main()
