from pymongo import MongoClient
import json
import yaml

MONGODB_URI = "mongodb://127.0.0.1:27017/"
COLLECTION_NAME = "mcqs"

client = MongoClient(MONGODB_URI)
db = client["data3"]

def store_mcqs(mcqs, output_format="json"):
    try:
        if output_format == "json":
            mcq_data = [json.loads(mcq) for mcq in mcqs]
        elif output_format == "yaml":
            mcq_data = [yaml.safe_load(mcq) for mcq in mcqs]
        else:
            print("Invalid output format specified.")
            return

        result = db[COLLECTION_NAME].insert_many(mcq_data)
        print(f"Stored {len(result.inserted_ids)} MCQs in MongoDB.")
    except Exception as e:
        print(f"Error storing MCQs in MongoDB: {e}")
