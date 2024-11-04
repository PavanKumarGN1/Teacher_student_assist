from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid

# MongoDB connection details
MONGODB_URI = "mongodb://127.0.0.1:27017/"
COLLECTION_NAME_MCQS = "mcqs"
COLLECTION_NAME_QA = "qa_pairs"

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client["msq_qa"]
    
    # Check if collections exist and create them if not
    if COLLECTION_NAME_MCQS not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME_MCQS)
        print(f"Collection '{COLLECTION_NAME_MCQS}' created.")
    else:
        print(f"Collection '{COLLECTION_NAME_MCQS}' already exists.")
    
    if COLLECTION_NAME_QA not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME_QA)
        print(f"Collection '{COLLECTION_NAME_QA}' created.")
    else:
        print(f"Collection '{COLLECTION_NAME_QA}' already exists.")
        
except ConnectionFailure:
    print("Could not connect to MongoDB. Please check the connection details.")
    exit(1)
except CollectionInvalid:
    print("Collection creation failed, it may already exist.")
    exit(1)

def store_mcqs(mcqs):
    """
    Store multiple-choice questions in MongoDB.
    
    Args:
        mcqs (list of dict): List of MCQs to store, where each MCQ is a dictionary.
    """
    try:
        if isinstance(mcqs, list):
            result = db[COLLECTION_NAME_MCQS].insert_many(mcqs)
            print(f"Stored {len(result.inserted_ids)} MCQs in MongoDB.")
        else:
            print("MCQs should be a list.")
    except Exception as e:
        print(f"Error storing MCQs in MongoDB: {e}")



def store_qa(questions_and_answers):
    """
    Store questions and answers in MongoDB.
    
    Args:
        questions_and_answers (list of dict): List of questions and answers to store, where each item is a dictionary.
    """
    try:
        if isinstance(questions_and_answers, list):
            result = db[COLLECTION_NAME_QA].insert_many(questions_and_answers)
            print(f"Stored {len(result.inserted_ids)} Q&A pairs in MongoDB.")
        else:
            print("Input should be a list.")
    except Exception as e:
        print(f"Error storing Q&A pairs in MongoDB: {e}")
