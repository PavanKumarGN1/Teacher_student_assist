import os
import time
from qdrant_client import QdrantClient

# Qdrant connection details (replace with your actual URL and API key or set them in environment variables)
QDRANT_URL = os.getenv('QDRANT_URL') or "your_qdrant_url_here"
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY') or "your_qdrant_api_key_here"

# Connect to Qdrant instance
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

def get_chunks_from_qdrant(collection_name):
    start_time = time.time()
    try:
        response = qdrant_client.scroll(collection_name=collection_name, with_payload=True)
        text_chunks = [hit.payload.get('text', '') for hit in response[0] if hit.payload.get('text', '')]
        
        end_time = time.time()
        print(f"Retrieved {len(text_chunks)} chunks from Qdrant in {end_time - start_time:.2f} seconds")
        
        if not text_chunks:
            print("No text chunks were found. Please verify the collection contains data with 'chunk' fields.")
        
        return text_chunks
    except Exception as e:
        print(f"Error retrieving chunks from Qdrant: {e}")
        return []
