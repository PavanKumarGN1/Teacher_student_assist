
import logging
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)

# Connect to MongoDB
def connect_to_mongo(db_name, collection_name):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[collection_name]
        logging.info("Connected to MongoDB.")
        return collection
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise

# Fetch documents from MongoDB
def fetch_documents(collection):
    try:
        documents = list(collection.find())
        logging.info(f"Fetched {len(documents)} documents from MongoDB.")
        return documents
    except Exception as e:
        logging.error(f"Error fetching documents: {e}")
        return []


# Initialize vector store
def initialize_vector_store(model, collection):
    try:
        vectors = []
        for doc in fetch_documents(collection):
            if 'question' in doc and 'options' in doc:
                question = doc['question']
                options = doc['options']
                answer = doc['correct_answer']
                vector = model.encode(question)
                vectors.append((vector, options, answer, doc))  # Store the entire doc
            else:
                logging.warning(f"Skipping document due to missing or invalid fields: {doc['_id']}")
        return vectors
    except Exception as e:
        logging.error(f"Error initializing vector store: {e}")
        return None

# Load the Sentence Transformer model
def load_model():
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model
    except Exception as e:
        logging.error(f"Error loading the model: {e}")
        return None

# Query the vector store
def query_vector_store(user_query, vector_store, model):
    try:
        query_vector = model.encode(user_query)
        similarities = []
        
        for vector, options, doc in vector_store:
            # Compute cosine similarity
            similarity = np.dot(query_vector, vector) / (np.linalg.norm(query_vector) * np.linalg.norm(vector))
            similarities.append((similarity, options, doc))
        
        # Sort by similarity and get the top match
        similarities.sort(key=lambda x: x[0], reverse=True)
        return similarities[0] if similarities else None  # Return the top result
    except Exception as e:
        logging.error(f"Error querying vector store: {e}")
        return None

# Main function to initialize backend
def main(db_name, collection_name):
    collection = connect_to_mongo(db_name, collection_name)
    model = load_model()
    vector_store = initialize_vector_store(model, collection)
    return model, vector_store
