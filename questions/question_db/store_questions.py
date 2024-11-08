from pymongo import MongoClient

# MongoDB connection details
MONGODB_URI = "mongodb://127.0.0.1:27017/data1"  # Replace with your actual database name
COLLECTION_NAME = "qa_collection"  # New collection name for questions and answers

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client["data4"]  # Replace with your actual database name

def store_questions(questions_and_answers):
    """
    Store questions and answers in MongoDB.
    
    Args:
        questions_and_answers (list of dict): List of questions and answers to store, where each item is a dictionary.
    """
    try:
        if isinstance(questions_and_answers, list):
            result = db[COLLECTION_NAME].insert_many(questions_and_answers)
            print(f"Stored {len(result.inserted_ids)} Q&A pairs in MongoDB.")
        else:
            print("Input should be a list.")
    except Exception as e:
        print(f"Error storing Q&A pairs in MongoDB: {e}")
