import os
import sys
import csv
import re
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

if len(sys.argv) != 4:
    print("Usage: python3 analyze_text_file.py <mongo_doc_id> <text_file_path> <output_dir>")
    sys.exit(1)

doc_id = sys.argv[1]
text_file_path = sys.argv[2]
output_dir = sys.argv[3]

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB_NAME", "text_library")
collection_name = os.environ.get("MONGO_COLLECTION_NAME", "texts")

if not mongo_uri:
    print("ERROR: MONGO_URI is not set.")
    sys.exit(1)

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

try:
    mongo_id = ObjectId(doc_id)

    if not os.path.exists(text_file_path):
        raise FileNotFoundError("Text file does not exist: " + text_file_path)

    os.makedirs(output_dir, exist_ok=True)

    with open(text_file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    words = re.findall(r"[A-Za-z']+", text.lower())

    word_count = len(words)
    unique_word_count = len(set(words))
    character_count = len(text)
    line_count = len(text.splitlines())

    if word_count > 0:
        average_word_length = sum(len(word) for word in words) / word_count
    else:
        average_word_length = 0

    positive_words = [
        "good", "great", "happy", "love", "hope", "best",
        "peace", "joy", "bright", "excellent", "beautiful"
    ]

    negative_words = [
        "bad", "sad", "hate", "fear", "death", "pain",
        "worst", "dark", "war", "terrible", "horrible"
    ]

    positive_count = 0
    negative_count = 0

    for word in words:
        if word in positive_words:
            positive_count = positive_count + 1
        if word in negative_words:
            negative_count = negative_count + 1

    if word_count > 0:
        sentiment_score = (positive_count - negative_count) / word_count
    else:
        sentiment_score = 0

    base_name = os.path.basename(text_file_path).replace(".txt", "")
    result_file_path = os.path.join(output_dir, base_name + "_analysis.csv")

    with open(result_file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "source_file",
            "result_file_path",
            "word_count",
            "unique_word_count",
            "character_count",
            "line_count",
            "average_word_length",
            "positive_word_count",
            "negative_word_count",
            "sentiment_score"
        ])

        writer.writerow([
            text_file_path,
            result_file_path,
            word_count,
            unique_word_count,
            character_count,
            line_count,
            average_word_length,
            positive_count,
            negative_count,
            sentiment_score
        ])

    summary_statistics = {
        "word_count": word_count,
        "unique_word_count": unique_word_count,
        "character_count": character_count,
        "line_count": line_count,
        "average_word_length": average_word_length,
        "positive_word_count": positive_count,
        "negative_word_count": negative_count,
        "sentiment_score": sentiment_score
    }

    collection.update_one(
        {"_id": mongo_id},
        {
            "$set": {
                "status": "completed",
                "result_file_path": result_file_path,
                "summary_statistics": summary_statistics,
                "analyzed_at": datetime.utcnow()
            }
        }
    )

    print("Analyzed:", text_file_path)
    print("Output CSV:", result_file_path)
    print("Word count:", word_count)
    print("Sentiment score:", sentiment_score)

except Exception as e:
    try:
        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {
                "$set": {
                    "status": "error",
                    "error_message": str(e),
                    "analyzed_at": datetime.utcnow()
                }
            }
        )
    except Exception:
        pass

    print("Error analyzing file:", text_file_path)
    print(e)
    sys.exit(1)