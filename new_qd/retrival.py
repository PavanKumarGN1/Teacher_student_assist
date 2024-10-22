# import os
# import streamlit as st
# from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient
# import requests
# import json
# import time

# # Load environment variables
# load_dotenv()

# # Load the embedding model
# model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# # Initialize Qdrant client
# api_key = os.getenv("QDRANT_API_KEY")  # Store your Qdrant API key in the environment
# qdrant_url = os.getenv("QDRANT_URL")  # Store your Qdrant URL in the environment
# llama_api_key = os.getenv("LLAMA_API_KEY")  # Get Llama API key from environment  
# llama_api_url = os.getenv("LLAMA_API_URL")  # Get Llama API URL from environment

# def get_qdrant_client():
#     try:
#         client = QdrantClient(api_key=api_key, url=qdrant_url)
#         client.get_collections()  # Test the connection
#         return client
#     except Exception as e:
#         st.error(f"Error connecting to Qdrant: {repr(e)}")
#         return None

# qdrant_client = get_qdrant_client()

# def count_tokens(text):
#     return len(text.split())

# def retrieve_top_chunks_from_qdrant(query, collection_name="text_chunks", top_k=10):
#     if qdrant_client is None:
#         st.error("Qdrant client is not initialized.")
#         return None
#     try:
#         query_vector = model.encode([query])[0].tolist()
#         search_result = qdrant_client.search(
#             collection_name=collection_name,
#             query_vector=query_vector,
#             limit=top_k
#         )
#         if search_result:
#             chunks = [res.payload['text'] for res in search_result]
#             return chunks
#         else:
#             st.warning("No results found in Qdrant.")
#             return None
#     except Exception as e:
#         st.error(f"Error retrieving from Qdrant: {e}")
#         return None

# def get_llama_response(query, context):
#     headers = {
#         'api-key': llama_api_key,
#         'Content-Type': 'application/json'
#     }
#     payload = {
#         "model": "meta-llama/Meta-Llama-3-8B-Instruct",
#         "max_tokens": "300",
#         "stream": False,
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "You are an intelligent AI assistant. Use ONLY the provided document context to accurately answer the user's question. If the context doesn't contain the answer, reply with 'The answer is not found in the provided context.' Do not provide any information that isn't explicitly stated in the context."
#             },
#             {
#                 "role": "user",
#                 "content": f"Question: {query}\n\nDocument Context: {context}"
#             }
#         ]
#     }
#     try:
#         response = requests.post(llama_api_url, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()
#         return response.json().get("choices")[0].get("message").get("content").strip()
#     except Exception as e:
#         st.error(f"Error calling Llama API: {e}")
#         return "The answer is not found in the provided context."

# def retrieve(query, collection_name):
#     chunks = retrieve_top_chunks_from_qdrant(query, collection_name)
#     if chunks:
#         context = "\n\n".join(chunks)
#         return get_llama_response(query, context)
#     return None






############################ for multiple docs ########################################



import os
import logging
import streamlit as st
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import requests
import json

# Load environment variables
api_key = os.getenv("QDRANT_API_KEY")  
qdrant_url = os.getenv("QDRANT_URL")  
llama_api_key = os.getenv("LLAMA_API_KEY")
llama_api_url = os.getenv("LLAMA_API_URL")

# Initialize SentenceTransformer model
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

def get_qdrant_client():
    """Connect to the Qdrant client."""
    try:
        client = QdrantClient(api_key=api_key, url=qdrant_url)
        client.get_collections()  # Test connection
        return client
    except Exception as e:
        st.error(f"Error connecting to Qdrant: {repr(e)}")
        return None

qdrant_client = get_qdrant_client()

def retrieve_top_chunks_from_qdrant(query, collection_name="text_chunks", top_k=10):
    """Retrieve top chunks from Qdrant based on the query."""
    if qdrant_client is None:
        st.error("Qdrant client is not initialized.")
        return None
    try:
        query_vector = model.encode([query])[0].tolist()
        search_result = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        if search_result:
            chunks = [res.payload['text'] for res in search_result]
            return chunks
        else:
            st.warning("No results found in Qdrant.")
            return None
    except Exception as e:
        st.error(f"Error retrieving from Qdrant: {e}")
        return None

def get_llama_response(query, context):
    """Call Llama API with the provided context and query."""
    headers = {
        'api-key': llama_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": "300",
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You are an intelligent AI assistant. Use ONLY the provided document context to answer the user's question accurately. If the context doesn't contain the answer, reply 'The answer is not found in the provided context.'"
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\nDocument Context: {context}"
            }
        ]
    }
    try:
        response = requests.post(llama_api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json().get("choices")[0].get("message").get("content").strip()
    except Exception as e:
        st.error(f"Error calling Llama API: {e}")
        return "The answer is not found in the provided context."

def retrieve(query, collection_name):
    """Retrieve the response based on the query."""
    chunks = retrieve_top_chunks_from_qdrant(query, collection_name)
    if chunks:
        context = "\n\n".join(chunks)
        return get_llama_response(query, context)
    return None
