# import streamlit as st
# import requests
# import json
# import fitz  # PyMuPDF
# import numpy as np
# from dotenv import load_dotenv
# import os
# from qdrant_client import QdrantClient
# from qdrant_client.http import models as qdrant_models

# # Load environment variables from .env file
# load_dotenv()
# API_URL = os.getenv('llama_api_url')
# API_KEY = os.getenv('llama_api_key')
# QDRANT_URL = os.getenv('QDRANT_URL')  # Qdrant endpoint URL
# QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')  # Qdrant API key

# # Connect to Qdrant instance
# qdrant_client = QdrantClient(
#     url=QDRANT_URL,
#     api_key=QDRANT_API_KEY,
# )

# HEADERS = {
#     'api-key': API_KEY,
#     'Content-Type': 'application/json'
# }

# # Function to extract text from PDF using PyMuPDF
# def extract_text_from_pdf(pdf_file):
#     try:
#         pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
#         text = ""
        
#         for page_num in range(pdf_document.page_count):
#             page = pdf_document[page_num]
#             text += page.get_text("text")
        
#         st.success("Document uploaded and text extracted successfully.")
#         return text
#     except Exception as e:
#         st.error(f"Failed to extract text from PDF: {str(e)}")
#         return None

# # Function to split document text into chunks (to handle token limits)
# def split_text_into_chunks(text, max_length=4000):
#     words = text.split()
#     chunks = []
#     current_chunk = []
#     current_length = 0

#     for word in words:
#         current_length += len(word) + 1  # +1 for the space
#         if current_length > max_length:
#             chunks.append(" ".join(current_chunk))
#             current_chunk = []
#             current_length = len(word) + 1
#         current_chunk.append(word)
    
#     if current_chunk:
#         chunks.append(" ".join(current_chunk))

#     return chunks

# # Function to generate embeddings for text using a pre-trained model
# def generate_embeddings(text):
#     # Replace this with actual embedding generation logic
#     return np.random.rand(768).astype('float32')  # Example: Random embeddings of size 768

# # Function to store embeddings in Qdrant
# def store_embeddings_in_qdrant(chunks):
#     # Create a collection in Qdrant if it doesn't exist
#     collection_name = "document_embeddings"
    
#     qdrant_client.recreate_collection(
#         collection_name=collection_name,
#         vectors_config=qdrant_models.VectorParams(
#             size=768,  # Size of embeddings
#             distance="Cosine"  # or "Euclidean", depending on your model
#         ),
#     )
    
#     for i, chunk in enumerate(chunks):
#         embedding = generate_embeddings(chunk)
#         qdrant_client.upsert(
#             collection_name=collection_name,
#             points=[
#                 qdrant_models.PointStruct(
#                     id=i,
#                     vector=embedding.tolist(),  # Convert numpy array to list
#                     payload={"chunk": chunk}  # Storing the chunk as metadata
#                 )
#             ]
#         )
    
#     st.success("Embeddings stored in Qdrant successfully.")

# # Function to generate a summary for a chunk using the LLM
# def generate_summary_for_chunk(chunk_content):
#     data = {
#         "model": "meta-llama/Meta-Llama-3-8B-Instruct",
#         "max_tokens": 400,
#         "stream": False,
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "This is a chat between a user and an artificial intelligence assistant."
#             },
#             {
#                 "role": "user",
#                 "content": f"Summarize the following document content: {chunk_content}"
#             }
#         ]
#     }

#     response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
#     if response.status_code == 200:
#         result = response.json()
#         summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
#         return summary
#     else:
#         st.error(f"Failed to generate summary: {response.text}")
#         return None

# # Function to generate teaching resources based on the summary
# def generate_resources(summary, task):
#     data = {
#         "model": "meta-llama/Meta-Llama-3-8B-Instruct",
#         "max_tokens": 500,
#         "stream": False,
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "This is a chat between a user and an artificial intelligence assistant."
#             },
#             {
#                 "role": "user",
#                 "content": f"{task} for the following summary: {summary}"
#             }
#         ]
#     }

#     response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
#     if response.status_code == 200:
#         result = response.json()
#         resources = result.get('choices', [{}])[0].get('message', {}).get('content', '')
#         return resources
#     else:
#         st.error(f"Failed to generate resources: {response.text}")
#         return None

# # Main Streamlit app
# def main():
#     st.title("Teacher and Student Assistance System")

#     # Sidebar for PDF upload
#     st.sidebar.header("Upload Educational Document")
#     uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

#     if uploaded_file is not None:
#         document_content = extract_text_from_pdf(uploaded_file)
        
#         if document_content:
#             # Step 2: Split document into chunks to handle token limits
#             chunks = split_text_into_chunks(document_content, max_length=7000)
#             st.header(f"Generating summary for {len(chunks)} chunk(s)...")

#             # Only generate summary if not already done
#             if "summary" not in st.session_state:
#                 complete_summary = ""
#                 for i, chunk in enumerate(chunks):
#                     st.write(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
#                     summary = generate_summary_for_chunk(chunk)
#                     if summary:
#                         complete_summary += summary + " "
                
#                 if complete_summary:
#                     st.session_state.summary = complete_summary
#                     # Store embeddings in Qdrant
#                     store_embeddings_in_qdrant(chunks)
#                     st.subheader("Generated Summary:")
#                     st.write(st.session_state.summary)
#             else:
#                 st.subheader("Previously Generated Summary:")
#                 st.write(st.session_state.summary)

#             # Duration input for planning tasks
#             duration_units = st.selectbox("Select the duration unit:", ["Minutes", "Hours", "Days", "Weeks", "Months"])
#             duration = st.number_input("Enter duration:", min_value=1, step=1)

#             # Create tabs for different tasks
#             tabs = st.tabs(["Teaching Guide", "Timetable Management", "Pedagogy Assistance", "Lesson Plan", "Resources"])

#             # Teaching Guide Tab
#             with tabs[0]:
#                 if st.button("Generate Teaching Guide"):
#                     teaching_guide = generate_resources(st.session_state.summary, "Create a detailed teaching guide")
#                     if teaching_guide:
#                         st.subheader("Generated Teaching Guide:")
#                         st.write(teaching_guide)

#             # Timetable Management Tab
#             with tabs[1]:
#                 if st.button("Generate Timetable Management"):
#                     timetable_management = generate_resources(st.session_state.summary, "Create a timetable management plan")
#                     if timetable_management:
#                         st.subheader("Generated Timetable Management:")
#                         st.write(timetable_management)

#             # Pedagogy Assistance Tab
#             with tabs[2]:
#                 if st.button("Generate Pedagogy Assistance"):
#                     pedagogy_assistance = generate_resources(st.session_state.summary, "Create a pedagogy assistance plan")
#                     if pedagogy_assistance:
#                         st.subheader("Generated Pedagogy Assistance:")
#                         st.write(pedagogy_assistance)

#             # Lesson Plan Tab
#             with tabs[3]:
#                 if st.button("Generate Lesson Plan"):
#                     lesson_plan = generate_resources(st.session_state.summary, "Create a lesson plan")
#                     if lesson_plan:
#                         st.subheader("Generated Lesson Plan:")
#                         st.write(lesson_plan)

#             # Resources Tab
#             with tabs[4]:
#                 if st.button("Generate Resources"):
#                     resources = generate_resources(st.session_state.summary, "Create teaching resources")
#                     if resources:
#                         st.subheader("Generated Resources:")
#                         st.write(resources)

# if __name__ == "__main__":
#     main()




import streamlit as st
import requests
import json
import fitz  # PyMuPDF
import numpy as np
from dotenv import load_dotenv
import os
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
    # Replace this with actual embedding generation logic
    return np.random.rand(768).astype('float32')  # Example: Random embeddings of size 768

# Function to store embeddings in Qdrant
def store_embeddings_in_qdrant(chunks):
    # Create a collection in Qdrant if it doesn't exist
    collection_name = "document_embeddings"
    
    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qdrant_models.VectorParams(
            size=768,  # Size of embeddings
            distance="Cosine"  # or "Euclidean", depending on your model
        ),
    )
    
    for i, chunk in enumerate(chunks):
        embedding = generate_embeddings(chunk)
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                qdrant_models.PointStruct(
                    id=i,
                    vector=embedding.tolist(),  # Convert numpy array to list
                    payload={"chunk": chunk}  # Storing the chunk as metadata
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
                    pedagogy_assistance = generate_resources(st.session_state.summary, "Create a pedagogy assistance plan", duration_units, duration)
                    if pedagogy_assistance:
                        st.subheader("Generated Pedagogy Assistance:")
                        st.write(pedagogy_assistance)

            # Lesson Plan Tab
            with tabs[3]:
                if st.button("Generate Lesson Plan"):
                    lesson_plan = generate_resources(st.session_state.summary, "Create a lesson plan", duration_units, duration)
                    if lesson_plan:
                        st.subheader("Generated Lesson Plan:")
                        st.write(lesson_plan)

            # Resources Tab
            with tabs[4]:
                if st.button("Generate Resources"):
                    resources = generate_resources(st.session_state.summary, "Create teaching resources", duration_units, duration)
                    if resources:
                        st.subheader("Generated Resources:")
                        st.write(resources)

if __name__ == "__main__":
    main()
