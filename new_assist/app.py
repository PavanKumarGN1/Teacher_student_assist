import os
import logging
import requests
import json
import streamlit as st
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from embeddings import store_text_in_qdrant

# Load environment variables
load_dotenv()

# Load the embedding model
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# Initialize logger
logging.basicConfig(level=logging.INFO)

# Llama API configurations
llama_api_key = os.getenv("LLAMA_API_KEY")
llama_api_url = os.getenv("LLAMA_API_URL")

# Create uploads directory if it doesn't exist
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)  # Create uploads directory if it does not exist

def retrieve_top_chunks_from_qdrant(query, collection_name="text_chunks", top_k=10):
    from qdrant_client import QdrantClient

    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        port=6333,
        timeout=120
    )

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
                "content": "You are an intelligent AI assistant. Use ONLY the provided document context to accurately answer the user's question. If the context doesn't contain the answer, reply with 'The answer is not found in the provided context.'"
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

# Streamlit App
st.title("Document Q&A Assistant")

# File upload
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    pdf_file_path = os.path.join(uploads_dir, uploaded_file.name)  # Use uploads_dir
    with open(pdf_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    collection_name = st.text_input("Enter collection name", value=uploaded_file.name.split('.')[0])
    
    if st.button("Store Text and Generate Summary"):
        store_text_in_qdrant(pdf_file_path, collection_name)
        st.success("Text has been stored in Qdrant.")
    
    query = st.text_input("Enter your query")
    
    if st.button("Get Answer"):
        if query:
            response, references = retrieve(query, collection_name)
            if response:
                st.write("Response from Llama:", response)
                st.write("References:", references)
            else:
                st.warning("No response found.")
        else:
            st.warning("Please enter a query.")
