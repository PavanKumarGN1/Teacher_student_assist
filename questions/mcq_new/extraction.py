import os
import time
from qdrant_client import QdrantClient

# Set Qdrant connection details
QDRANT_URL = os.getenv('QDRANT_URL', 'your_qdrant_url_here')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', 'your_qdrant_api_key_here')

# Connect to Qdrant instance
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
collection_name = "document_embeddings"

def get_chunks_from_qdrant(collection_name):
    start_time = time.time()
    try:
        response, _ = qdrant_client.scroll(collection_name=collection_name, with_payload=True)
        # Print raw response for debugging
        print("Raw response from Qdrant:", response[:3])  # Log only the first few entries
        text_chunks = [hit.payload.get('chunk', '') for hit in response if hit.payload.get('chunk', '')]
        end_time = time.time()
        print(f"Retrieved {len(text_chunks)} chunks from Qdrant")
        print(f"Time taken to retrieve chunks: {end_time - start_time:.2f} seconds")
        return text_chunks
    except Exception as e:
        print(f"Error retrieving chunks from Qdrant: {e}")
        return []
