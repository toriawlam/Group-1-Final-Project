import os
import sys
import json
from pymongo import MongoClient

def get_collection():
    """Connects to MongoDB using environment variables."""
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("MONGO_DB_NAME")
    collection_name = os.environ.get("MONGO_COLLECTION_NAME")

    if not mongo_uri or not db_name or not collection_name:
        print("Error: Missing database environment variables.")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db[collection_name]

def show_pipeline_summary(collection):
    """Prints a high-level summary of the entire database."""
    total_docs = collection.count_documents({})
    unprocessed = collection.count_documents({"status": "unprocessed"})
    processing = collection.count_documents({"status": "processing"})
    completed = collection.count_documents({"status": "completed"})

    print("\n" + "="*30)
    print(" PIPELINE STATUS SUMMARY")
    print("="*30)
    print(f"Total Texts Tracked: {total_docs}")
    print(f"  - Unprocessed: {unprocessed}")
    print(f"  - Processing:  {processing}")
    print(f"  - Completed:   {completed}")
    print("="*30 + "\n")

def search_specific_url(collection, search_url):
    """Finds and prints the details for a specific URL."""
    doc = collection.find_one({"url": search_url}, {"_id": 0}) # _id: 0 hides the messy MongoDB object ID

    if not doc:
        print(f"\nNo record found for URL: {search_url}\n")
        return

    print("\n" + "="*30)
    print(" RECORD DETAILS")
    print("="*30)
    
    # Print the basic info
    print(f"URL: {doc.get('url')}")
    print(f"Status: {doc.get('status').upper()}")
    print(f"Added At: {doc.get('added_at')}")

    # If Step 5 has added analysis metrics, print them out nicely
    if "analysis_results" in doc:
        print("\n--- Analysis Metrics ---")
        # Pretty print the dictionary of results
        print(json.dumps(doc["analysis_results"], indent=4))
    elif doc.get("status") == "completed":
        print("\nStatus is completed, but no analysis metrics were found.")
    else:
        print("\nAnalysis pending...")
        
    print("="*30 + "\n")

def main():
    collection = get_collection()

    # If the user runs `python query_results.py` (no arguments)
    if len(sys.argv) == 1:
        show_pipeline_summary(collection)
        
    # If the user runs `python query_results.py <url>` (1 argument)
    elif len(sys.argv) == 2:
        search_url = sys.argv[1].strip()
        search_specific_url(collection, search_url)
        
    # If they passed too many arguments
    else:
        print("Usage:")
        print("  View summary: python3 query_results.py")
        print("  Search URL:   python3 query_results.py <url>")
        sys.exit(1)

if __name__ == "__main__":
    main()