# import streamlit as st
# import requests
# import json
# import fitz  # PyMuPDF
# import numpy as np
# from dotenv import load_dotenv
# import os
# import pandas as pd
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
#     return np.random.rand(768).astype('float32')  # Example: Random embeddings of size 768

# # Function to store embeddings in Qdrant
# def store_embeddings_in_qdrant(chunks):
#     collection_name = "document_embeddings"
    
#     qdrant_client.recreate_collection(
#         collection_name=collection_name,
#         vectors_config=qdrant_models.VectorParams(
#             size=768,
#             distance="Cosine"
#         ),
#     )
    
#     for i, chunk in enumerate(chunks):
#         embedding = generate_embeddings(chunk)
#         qdrant_client.upsert(
#             collection_name=collection_name,
#             points=[
#                 qdrant_models.PointStruct(
#                     id=i,
#                     vector=embedding.tolist(),
#                     payload={"chunk": chunk}
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

# # Function to generate multiple questions and answers based on summary
# def generate_questions_and_answers(summary):
#     data = {
#         "model": "meta-llama/Meta-Llama-3-8B-Instruct",
#         "max_tokens": 800,
#         "stream": False,
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "This is a chat between a user and an artificial intelligence assistant."
#             },
#             {
#                 "role": "user",
#                 "content": f"Generate multiple questions and answers from the following summary: {summary}"
#             }
#         ]
#     }

#     response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
#     if response.status_code == 200:
#         result = response.json()
#         qna = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
#         if qna:
#             return parse_qna(qna)
#         else:
#             st.error("No Q&A text found in the response.")
#             return None
#     else:
#         st.error(f"Failed to generate Q&A: {response.text}")
#         return None

# # Function to parse Q&A text into structured format
# def parse_qna(qna_text):
#     qna_pairs = []
#     lines = qna_text.strip().split("\n")
#     current_question, current_answer = None, None
#     for line in lines:
#         if line.startswith("Q"):
#             if current_question and current_answer:
#                 qna_pairs.append((current_question, current_answer))
#             current_question = line.replace("Q:", "").strip()
#             current_answer = ""
#         elif line.startswith("A") and current_question:
#             current_answer = line.replace("A:", "").strip()
#             qna_pairs.append((current_question, current_answer))
#             current_question, current_answer = None, None

#     if not qna_pairs:
#         st.warning("Q&A parsing failed or returned empty.")
#     return qna_pairs

# # Function to save Q&A to an Excel file
# def save_qna_to_excel(qna_pairs):
#     df = pd.DataFrame(qna_pairs, columns=["Question", "Answer"])
#     excel_path = "q_a1.xlsx"
#     df.to_excel(excel_path, index=False)
#     return excel_path

# # Main Streamlit app
# def main():
#     st.title("Teacher and Student Assistance System")

#     # Sidebar for PDF upload
#     st.sidebar.header("Upload Educational Document")
#     uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

#     if uploaded_file is not None:
#         document_content = extract_text_from_pdf(uploaded_file)
        
#         if document_content:
#             chunks = split_text_into_chunks(document_content, max_length=7000)
#             st.header(f"Generating summary for {len(chunks)} chunk(s)...")

#             complete_summary = ""
#             for i, chunk in enumerate(chunks):
#                 st.write(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
#                 summary = generate_summary_for_chunk(chunk)
#                 if summary:
#                     complete_summary += summary + " "
                
#             st.session_state.summary = complete_summary
#             store_embeddings_in_qdrant(chunks)
#             st.subheader("Generated Summary:")
#             st.write(st.session_state.summary)

#     if st.sidebar.button("Generate Questions and Answers"):
#         if "summary" in st.session_state:
#             qna_pairs = generate_questions_and_answers(st.session_state.summary)
#             if qna_pairs:
#                 st.write("Generated Questions and Answers:")
#                 for q, a in qna_pairs:
#                     st.write(f"Q: {q}\nA: {a}\n")

#                 # Save Q&A to Excel
#                 excel_path = save_qna_to_excel(qna_pairs)
#                 st.success(f"Q&A saved to {excel_path}. You can download it below.")
#                 st.download_button("Download Q&A Excel", data=open(excel_path, "rb").read(), file_name="Q&A.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# if __name__ == "__main__":
#     main()





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
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

# Connect to Qdrant instance
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

HEADERS = {
    'api-key': API_KEY,
    'Content-Type': 'application/json'
}

# Function to extract text from PDF
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

# Function to split text into chunks
def split_text_into_chunks(text, max_length=4000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_length += len(word) + 1
        if current_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = len(word) + 1
        current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Generate embeddings for text
def generate_embeddings(text):
    return np.random.rand(768).astype('float32')  # Example: Random embeddings

# Store embeddings in Qdrant
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

# Generate summary for each chunk
def generate_summary_for_chunk(chunk_content):
    data = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 400,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "This is a chat between a user and an AI assistant."
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

# Generate Q&A and MCQs
def generate_questions_and_mcqs(summary):
    data = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 1200,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "This is a chat between a user and an AI assistant."
            },
            {
                "role": "user",
                "content": f"Generate both regular questions and multiple-choice questions (MCQs) from the following summary. Format the MCQs as:\nMCQ: [Question]\nOption 1: [Option]\nOption 2: [Option]\nOption 3: [Option]\nOption 4: [Option]\nAnswer: [Correct Option]\n\nSummary: {summary}"
            }
        ]
    }
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        qna_mcqs = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return parse_qna_mcqs(qna_mcqs)
    else:
        st.error(f"Failed to generate Q&A and MCQs: {response.text}")
        return None, None

# Parse Q&A and MCQ responses
# Parse Q&A and MCQ responses
def parse_qna_mcqs(qna_mcqs_text):
    qna_pairs = []
    mcq_pairs = []
    lines = qna_mcqs_text.strip().split("\n")
    current_question, current_answer = None, None
    current_mcq = {"question": "", "options": [], "answer": ""}

    for line in lines:
        line = line.strip()
        if line.startswith("Q:"):
            if current_question and current_answer:
                qna_pairs.append((current_question, current_answer))
            current_question = line.replace("Q:", "").strip()
            current_answer = ""
        elif line.startswith("A:") and current_question:
            current_answer = line.replace("A:", "").strip()
            qna_pairs.append((current_question, current_answer))
            current_question, current_answer = None, None
        elif line.startswith("MCQ:"):
            if current_mcq["question"]:  # Add the previous MCQ if exists
                mcq_pairs.append(current_mcq.copy())
            current_mcq = {"question": line.replace("MCQ:", "").strip(), "options": [], "answer": ""}
        elif line.startswith("Option"):
            option_text = line.split(":")[1].strip()
            current_mcq["options"].append(option_text)
        elif line.startswith("Answer:"):
            current_mcq["answer"] = line.split(":")[1].strip()
            mcq_pairs.append(current_mcq.copy())  # Add the last MCQ after processing

    # To handle the last question in case it wasn't added
    if current_question and current_answer:
        qna_pairs.append((current_question, current_answer))
    if current_mcq["question"]:  # Add the last MCQ if it exists
        mcq_pairs.append(current_mcq.copy())

    return qna_pairs, mcq_pairs


# Save Q&A and MCQs to Excel
def save_qna_mcqs_to_excel(qna_pairs, mcq_pairs):
    qna_df = pd.DataFrame(qna_pairs, columns=["Question", "Answer"])
    mcq_df = pd.DataFrame(mcq_pairs)
    with pd.ExcelWriter("Q&A_MCQs.xlsx") as writer:
        qna_df.to_excel(writer, sheet_name="Q&A", index=False)
        mcq_df.to_excel(writer, sheet_name="MCQs", index=False)
    return "Q&A_MCQs.xlsx"

# Main Streamlit app
def main():
    st.title("Teacher and Student Assistance System")
    st.sidebar.header("Upload Educational Document")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        document_content = extract_text_from_pdf(uploaded_file)
        
        if document_content:
            chunks = split_text_into_chunks(document_content, max_length=7000)
            st.header(f"Generating summary for {len(chunks)} chunk(s)...")

            complete_summary = ""
            for i, chunk in enumerate(chunks):
                st.write(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
                summary = generate_summary_for_chunk(chunk)
                if summary:
                    complete_summary += summary + " "
                
            st.session_state.summary = complete_summary
            store_embeddings_in_qdrant(chunks)
            st.subheader("Generated Summary:")
            st.write(st.session_state.summary)

    if st.sidebar.button("Generate Q&A and MCQs"):
        if "summary" in st.session_state:
            qna_pairs, mcq_pairs = generate_questions_and_mcqs(st.session_state.summary)
            if qna_pairs:
                st.write("Generated Questions and Answers:")
                for q, a in qna_pairs:
                    st.write(f"Q: {q}\nA: {a}\n")
            if mcq_pairs:
                st.write("Generated MCQs:")
                for mcq in mcq_pairs:
                    st.write(f"MCQ: {mcq['question']}")
                    for i, option in enumerate(mcq['options'], start=1):
                        st.write(f"Option {i}: {option}")
                    st.write(f"Answer: {mcq['answer']}\n")
                
                excel_path = save_qna_mcqs_to_excel(qna_pairs, mcq_pairs)
                st.success(f"Q&A and MCQs saved to {excel_path}. You can download it below.")
                st.download_button("Download Q&A and MCQs Excel", data=open(excel_path, "rb").read(), file_name="Q&A_MCQs.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()


