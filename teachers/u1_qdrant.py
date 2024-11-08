import streamlit as st
import requests
import json
import fitz  # PyMuPDF
import numpy as np
from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from sentence_transformers import SentenceTransformer

# Load environment variables from .env file
load_dotenv()
API_URL = os.getenv('llama_api_url')
API_KEY = os.getenv('llama_api_key')
QDRANT_URL = os.getenv('QDRANT_URL')  # Qdrant endpoint URL
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')  # Qdrant API key

# Connect to Qdrant instance
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# Load SentenceTransformer model
embedding_model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

HEADERS = {
    'api-key': API_KEY,
    'Content-Type': 'application/json'
}

# Function to extract text from PDF using PyMuPDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text("text")
        st.success("Document uploaded and text extracted successfully.")
        return text
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {str(e)}")
        return None

# Function to split document text into chunks (to handle token limits)
def split_text_into_chunks(text, max_length=4000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_length += len(word) + 1  # +1 for the space
        if current_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = len(word) + 1
        current_chunk.append(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Function to generate embeddings for text using SentenceTransformer
def generate_embeddings(text):
    embeddings = embedding_model.encode(text, convert_to_tensor=True)
    return embeddings.numpy().astype('float32')  # Convert to numpy array of float32

# Function to store embeddings in Qdrant
def store_embeddings_in_qdrant(chunks):
    collection_name = "document_embeddings"
    
    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qdrant_models.VectorParams(
            size=384,  # Size of embeddings for the MiniLM model
            distance="Cosine"
        ),
    )
    
    for i, chunk in enumerate(chunks):
        embedding = generate_embeddings(chunk)
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                qdrant_models.PointStruct(
                    id=i,
                    vector=embedding.tolist(),
                    payload={"chunk": chunk}
                )
            ]
        )
    
    st.success("Embeddings stored in Qdrant successfully.")

# Function to retrieve embeddings from Qdrant
# Function to retrieve embeddings from Qdrant
def retrieve_embeddings_from_qdrant():
    collection_name = "document_embeddings"
    result, _ = qdrant_client.scroll(collection_name=collection_name, limit=1000)  # Unpack the tuple
    return result  # 'result' contains the list of points

# Function to generate a summary for a chunk using the LLM
def generate_summary_for_chunk(chunk_content):
    data = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 400,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "This is a chat between a user and an artificial intelligence assistant."
            },
            {
                "role": "user",
                "content": f"Summarize the following document content: {chunk_content}"
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return summary
        else:
            st.error(f"Failed to generate summary: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error during API call: {str(e)}")
        return None
    
# Function to generate teaching resources based on the summary and duration
def generate_resources(summary, task, duration_units, duration):
    data = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 500,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "This is a chat between a user and an artificial intelligence assistant."
            },
            {
                "role": "user",
                "content": f"{task} based on the following summary for a duration of {duration} {duration_units}: {summary}"
            }
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        resources = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return resources
    else:
        st.error(f"Failed to generate resources: {response.text}")
        return None

# Main Streamlit app
def main():
    st.title("Teacher and Student Assistance System")

    # Sidebar for PDF upload and duration input
    st.sidebar.header("Upload Educational Document")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

    # Sidebar for duration input
    st.sidebar.header("Task Duration")
    duration_units = st.sidebar.selectbox("Select the duration unit:", ["Minutes", "Hours", "Days", "Weeks", "Months"])
    duration = st.sidebar.number_input("Enter duration:", min_value=1, step=1)

    if uploaded_file is not None:
        document_content = extract_text_from_pdf(uploaded_file)

        if document_content:
            # Step 2: Split document into chunks to handle token limits
            chunks = split_text_into_chunks(document_content, max_length=7000)
            st.header(f"Storing {len(chunks)} chunk(s) in Qdrant...")

            # Store embeddings in Qdrant
            store_embeddings_in_qdrant(chunks)

            # Create tabs for different tasks
            tab_names = ["Teaching Guide", "Timetable Management", "Pedagogy Assistance", "Lesson Plan", "Resources"]
            tabs = st.tabs(tab_names)

            # Teaching Guide Tab
            with tabs[0]:
                if st.button("Generate Teaching Guide"):
                    with st.spinner("Generating Teaching Guide..."):
                        embeddings = retrieve_embeddings_from_qdrant()
                        complete_summary = ""
                        for point in embeddings:
                            chunk_content = point.payload.get("chunk", "")
                            summary = generate_summary_for_chunk(chunk_content)
                            if summary:
                                complete_summary += summary + " "

                        if complete_summary:
                            st.subheader("Generated Teaching Guide:")
                            st.write(complete_summary)
                        else:
                            st.error("No summary was generated. Please check the API and try again.")

            # Timetable Management Tab
            with tabs[1]:
                if st.button("Generate Timetable Management"):
                    with st.spinner("Generating Timetable Management..."):
                        embeddings = retrieve_embeddings_from_qdrant()
                        complete_summary = ""
                        for point in embeddings:
                            chunk_content = point.payload.get("chunk", "")
                            summary = generate_summary_for_chunk(chunk_content)
                            if summary:
                                complete_summary += summary + " "
                        if complete_summary:
                            timetable_management = generate_resources(complete_summary, "Create a timetable management plan", duration_units, duration)
                            if timetable_management:
                                st.subheader("Generated Timetable Management:")
                                st.write(timetable_management)

            # Pedagogy Assistance Tab
            with tabs[2]:
                if st.button("Generate Pedagogy Assistance"):
                    with st.spinner("Generating Pedagogy Assistance..."):
                        embeddings = retrieve_embeddings_from_qdrant()
                        complete_summary = ""
                        for point in embeddings:
                            chunk_content = point.payload.get("chunk", "")
                            summary = generate_summary_for_chunk(chunk_content)
                            if summary:
                                complete_summary += summary + " "
                        if complete_summary:
                            pedagogy_assistance = generate_resources(complete_summary, "Generate pedagogy assistance", duration_units, duration)
                            if pedagogy_assistance:
                                st.subheader("Generated Pedagogy Assistance:")
                                st.write(pedagogy_assistance)

            # Lesson Plan Tab
            with tabs[3]:
                if st.button("Generate Lesson Plan"):
                    with st.spinner("Generating Lesson Plan..."):
                        embeddings = retrieve_embeddings_from_qdrant()
                        complete_summary = ""
                        for point in embeddings:
                            chunk_content = point.payload.get("chunk", "")
                            summary = generate_summary_for_chunk(chunk_content)
                            if summary:
                                complete_summary += summary + " "
                        if complete_summary:
                            lesson_plan = generate_resources(complete_summary, "Create a lesson plan", duration_units, duration)
                            if lesson_plan:
                                st.subheader("Generated Lesson Plan:")
                                st.write(lesson_plan)

            # Resources Tab
            with tabs[4]:
                if st.button("Generate Resources"):
                    with st.spinner("Generating Resources..."):
                        embeddings = retrieve_embeddings_from_qdrant()
                        complete_summary = ""
                        for point in embeddings:
                            chunk_content = point.payload.get("chunk", "")
                            summary = generate_summary_for_chunk(chunk_content)
                            if summary:
                                complete_summary += summary + " "
                        if complete_summary:
                            resources = generate_resources(complete_summary, "Generate educational resources", duration_units, duration)
                            if resources:
                                st.subheader("Generated Resources:")
                                st.write(resources)

if __name__ == "__main__":
    main()
