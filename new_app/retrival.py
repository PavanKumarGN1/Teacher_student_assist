# ############################ for multiple docs ########################################



# import os
# import logging
# import streamlit as st
# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# import requests
# import json

# # Load environment variables
# api_key = os.getenv("QDRANT_API_KEY")  
# qdrant_url = os.getenv("QDRANT_URL")  
# llama_api_key = os.getenv("LLAMA_API_KEY")
# llama_api_url = os.getenv("LLAMA_API_URL")

# # Initialize SentenceTransformer model
# model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# def get_qdrant_client():
#     """Connect to the Qdrant client."""
#     try:
#         client = QdrantClient(api_key=api_key, url=qdrant_url)
#         client.get_collections()  # Test connection
#         return client
#     except Exception as e:
#         st.error(f"Error connecting to Qdrant: {repr(e)}")
#         return None

# qdrant_client = get_qdrant_client()

# def retrieve_top_chunks_from_qdrant(query, collection_name="text_chunks", top_k=10):
#     """Retrieve top chunks from Qdrant based on the query."""
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
#     """Call Llama API with the provided context and query."""
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
#                 "content": "You are an intelligent AI assistant. Use ONLY the provided document context to answer the user's question accurately. If the context doesn't contain the answer, reply 'The answer is not found in the provided context.'"
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
#     """Retrieve the response based on the query."""
#     chunks = retrieve_top_chunks_from_qdrant(query, collection_name)
#     if chunks:
#         context = "\n\n".join(chunks)
#         return get_llama_response(query, context)
#     return None




# retrival.py


import os
import logging
import requests
import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the embedding model
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    port=6333,
    timeout=120
)

# Llama API configurations
llama_api_key = os.getenv("LLAMA_API_KEY")
llama_api_url = os.getenv("LLAMA_API_URL")

def retrieve_top_chunks_from_qdrant(query, collection_name="text_chunks", top_k=10):
    if qdrant_client is None:
        logging.error("Qdrant client is not initialized.")
        return None

    try:
        query_vector = model.encode([query])[0].tolist()

        logging.info(f"Query: {query}")
        search_result = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k
        )

        if search_result:
            chunks_with_metadata = [
                {
                    "text": res.payload['text'],
                    "document": res.payload['document'],
                    "page": res.payload['page']
                }
                for res in search_result
            ]
            logging.info(f"Chunks retrieved: {chunks_with_metadata}")
            return chunks_with_metadata
        else:
            logging.warning("No results found in Qdrant.")
            return None
    except Exception as e:
        logging.error(f"Error retrieving from Qdrant: {e}")
        return None

def get_llama_response(query, context):
    headers = {
        'api-key': llama_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 500,  # Increased token limit for a more detailed response
        "messages": [
            {
                "role": "system",
                "content": "You are an intelligent AI assistant. Use ONLY the provided document context to accurately answer the user's question. If the context doesn't contain the answer, reply with 'The answer is not found in the provided context.'\nAnd also you are capable of providing summaries of the document. Do not provide any information that isn't explicitly stated in the context."
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
        logging.error(f"Error calling Llama API: {e}")
        return "The answer is not found in the provided context."

def retrieve(query, collection_name):
    chunks = retrieve_top_chunks_from_qdrant(query, collection_name)
    if chunks:
        context = "\n\n".join(chunk['text'] for chunk in chunks)
        response = get_llama_response(query, context)
        
        # Include the source documents and pages
        references = {}
        for chunk in chunks:
            doc_name = chunk['document']
            page_num = chunk['page']
            if doc_name not in references:
                references[doc_name] = []
            references[doc_name].append(page_num)
        
        return response, references  # Ensure references is returned as a dictionary
    return None, {}
