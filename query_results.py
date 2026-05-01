import os
from pymongo import MongoClient

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB_NAME", "text_library")
collection_name = os.environ.get("MONGO_COLLECTION_NAME", "texts")

if not mongo_uri:
    print("ERROR: MONGO_URI is not set.")
    exit()

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

total_count = collection.count_documents({})
unprocessed_count = collection.count_documents({"status": "unprocessed"})
processing_count = collection.count_documents({"status": "processing"})
completed_count = collection.count_documents({"status": "completed"})
analyzed_count = collection.count_documents({"status": "analyzed"})
error_count = collection.count_documents({"status": "error"})

print("==============================")
print("PIPELINE STATUS SUMMARY")
print("==============================")
print("Total Texts Tracked:", total_count)
print("- Unprocessed:", unprocessed_count)
print("- Processing:", processing_count)
print("- Completed:", completed_count)
print("- Analyzed:", analyzed_count)
print("- Errors:", error_count)
print("==============================")

print("\nCOMPLETED / ANALYZED RECORDS")
print("==============================")

completed_records = collection.find({
    "$or": [
        {"status": "completed"},
        {"status": "analyzed"}
    ]
})

for doc in completed_records:
    print("Source:", doc.get("source_file_path", doc.get("url", "N/A")))
    print("Result CSV:", doc.get("result_file_path", "N/A"))
    print("Summary:", doc.get("summary_statistics", "N/A"))
    print("------------------------------")

print("\nUNPROCESSED RECORDS")
print("==============================")

unprocessed_records = collection.find({"status": "unprocessed"})

for doc in unprocessed_records:
    print("Source:", doc.get("source_file_path", doc.get("url", "N/A")))
    print("Document ID:", doc.get("_id"))
    print("------------------------------")
