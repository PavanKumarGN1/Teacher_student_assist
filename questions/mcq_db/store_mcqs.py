# # Generating.py

from pymongo import MongoClient

# MongoDB connection details
MONGODB_URI = "mongodb://127.0.0.1:27017/data1"  # Replace with your actual database name
COLLECTION_NAME = "mcqs"  # Collection name where MCQs will be stored

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client["data3"]  # Replace with your actual database name

def store_mcqs(mcqs):
    """
    Store multiple-choice questions in MongoDB.
    
    Args:
        mcqs (list of dict): List of MCQs to store, where each MCQ is a dictionary.
    """
    try:
        if isinstance(mcqs, list):
            result = db[COLLECTION_NAME].insert_many(mcqs)
            print(f"Stored {len(result.inserted_ids)} MCQs in MongoDB.")
        else:
            print("MCQs should be a list.")
    except Exception as e:
        print(f"Error storing MCQs in MongoDB: {e}")