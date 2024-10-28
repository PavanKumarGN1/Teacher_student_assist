import streamlit as st
import requests
import json
import fitz  # PyMuPDF
import numpy as np
from dotenv import load_dotenv
import os
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

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

# Function to generate embeddings for text using a pre-trained model
def generate_embeddings(text):
    return np.random.rand(768).astype('float32')  # Example: Random embeddings of size 768

# Function to store embeddings in Qdrant
def store_embeddings_in_qdrant(chunks):
    collection_name = "document_embeddings"
    
    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qdrant_models.VectorParams(
            size=768,
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

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return summary
    else:
        st.error(f"Failed to generate summary: {response.text}")
        return None

# Function to generate questions and answers based on summary
def generate_questions_and_answers(summary):
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
                "content": f"Generate at least 10 questions and their answers from the following summary: {summary}"
            }
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        qna = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return parse_qna(qna)
    else:
        st.error(f"Failed to generate Q&A: {response.text}")
        return None

# Function to parse the Q&A text into a structured format
def parse_qna(qna_text):
    lines = qna_text.strip().split("\n")
    qna_pairs = []
    for line in lines:
        if line.startswith("Q"):
            question = line.split(": ")[1].strip()
            answer = next((l.split(": ")[1].strip() for l in lines if l.startswith("A") and l.split(": ")[0] == f"A{len(qna_pairs)+1}"), "")
            qna_pairs.append((question, answer))
    return qna_pairs

# Function to save Q&A to an Excel file in the backend
def save_qna_to_excel(qna_pairs):
    df = pd.DataFrame(qna_pairs, columns=["Question", "Answer"])
    excel_path = "questions_and_answers.xlsx"  # Path to save the file
    df.to_excel(excel_path, index=False)  # Save the file
    return excel_path  # Return the path for further processing

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

    # Sidebar button to generate Questions and Answers
    if st.sidebar.button("Generate Questions and Answers"):
        if "summary" in st.session_state:
            qna_pairs = generate_questions_and_answers(st.session_state.summary)
            if qna_pairs:
                excel_path = save_qna_to_excel(qna_pairs)
                st.success("Q&A generated and saved to Excel file.")
                st.write(f"[Download Questions and Answers Excel file]({excel_path})")
            else:
                st.error("No Q&A generated.")

    if uploaded_file is not None:
        document_content = extract_text_from_pdf(uploaded_file)
        
        if document_content:
            # Step 2: Split document into chunks to handle token limits
            chunks = split_text_into_chunks(document_content, max_length=7000)
            st.header(f"Generating summary for {len(chunks)} chunk(s)...")

            # Only generate summary if not already done
            if "summary" not in st.session_state:
                complete_summary = ""
                for i, chunk in enumerate(chunks):
                    st.write(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
                    summary = generate_summary_for_chunk(chunk)
                    if summary:
                        complete_summary += summary + " "
                
                if complete_summary:
                    st.session_state.summary = complete_summary
                    # Store embeddings in Qdrant
                    store_embeddings_in_qdrant(chunks)
                    st.subheader("Generated Summary:")
                    st.write(st.session_state.summary)
            else:
                st.subheader("Previously Generated Summary:")
                st.write(st.session_state.summary)

            # Create tabs for different tasks
            tabs = st.tabs(["Teaching Guide", "Timetable Management", "Pedagogy Assistance", "Lesson Plan", "Resources"])

            # Teaching Guide Tab
            with tabs[0]:
                if st.button("Generate Teaching Guide"):
                    teaching_guide = generate_resources(st.session_state.summary, "Create a detailed teaching guide", duration_units, duration)
                    if teaching_guide:
                        st.subheader("Generated Teaching Guide:")
                        st.write(teaching_guide)

            # Timetable Management Tab
            with tabs[1]:
                if st.button("Generate Timetable Management"):
                    timetable_management = generate_resources(st.session_state.summary, "Create a timetable management plan", duration_units, duration)
                    if timetable_management:
                        st.subheader("Generated Timetable Management:")
                        st.write(timetable_management)

            # Pedagogy Assistance Tab
            with tabs[2]:
                if st.button("Generate Pedagogy Assistance"):
                    pedagogy_assistance = generate_resources(st.session_state.summary, "Provide pedagogy assistance", duration_units, duration)
                    if pedagogy_assistance:
                        st.subheader("Generated Pedagogy Assistance:")
                        st.write(pedagogy_assistance)

            # Lesson Plan Tab
            with tabs[3]:
                if st.button("Generate Lesson Plan"):
                    lesson_plan = generate_resources(st.session_state.summary, "Generate a lesson plan", duration_units, duration)
                    if lesson_plan:
                        st.subheader("Generated Lesson Plan:")
                        st.write(lesson_plan)

            # Resources Tab
            with tabs[4]:
                if st.button("Generate Resources"):
                    resources = generate_resources(st.session_state.summary, "Generate resources for", duration_units, duration)
                    if resources:
                        st.subheader("Generated Resources:")
                        st.write(resources)
if __name__ == "__main__":
    main()
