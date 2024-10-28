import os
import streamlit as st
import requests
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
LLAMA_API_URL = os.getenv('llama_api_url')
LLAMA_API_KEY = os.getenv('llama_api_key')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf = PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to generate summary for text chunks
def generate_summary_for_chunk(chunk):
    headers = {"Authorization": f"Bearer {LLAMA_API_KEY}"}
    response = requests.post(
        f"{LLAMA_API_URL}/summarize",
        headers=headers,
        json={"text": chunk}
    )
    
    # Check if the response was successful
    if response.status_code == 200:
        # Attempt to retrieve summary
        response_json = response.json()
        if 'summary' in response_json:
            return response_json["summary"]
        else:
            st.error("Summary not found in the response.")
            st.write(response_json)  # Display the full response for debugging
            return "Summary generation failed."
    else:
        st.error(f"Error generating summary: {response.status_code} - {response.text}")
        return "Summary generation failed."

# Function to generate questions and answers
def generate_questions_and_answers(summary):
    headers = {"Authorization": f"Bearer {LLAMA_API_KEY}"}
    response = requests.post(
        f"{LLAMA_API_URL}/generate_qna",
        headers=headers,
        json={"text": summary}
    )
    return parse_qna(response.json()["content"])

# Function to parse questions and answers from response
def parse_qna(qna_content):
    qna_pairs = []
    lines = qna_content.strip().split("\n")
    for line in lines:
        try:
            question, answer = line.split(":", 1)
            question = question.strip()
            answer = answer.strip()
            qna_pairs.append((question, answer))
        except ValueError:
            continue  # Ignore lines that don't contain a question and answer
    return qna_pairs

# Function to save Q&A pairs to Excel
def save_qna_to_excel(qna_pairs):
    df = pd.DataFrame(qna_pairs, columns=["Question", "Answer"])
    df.to_excel("qna_pairs.xlsx", index=False)

# Streamlit application
def main():
    st.title("Teacher and Student Assistance System")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract text from the uploaded PDF
        extracted_text = extract_text_from_pdf("temp.pdf")
        st.write("Extracted Text:")
        st.text_area("Text Preview", extracted_text, height=300)

        if st.button("Generate Summary and Q&A"):
            # Split text into manageable chunks
            text_chunks = [extracted_text[i:i + 2000] for i in range(0, len(extracted_text), 2000)]
            complete_summary = ""

            # Generate summary for each chunk
            for chunk in text_chunks:
                summary = generate_summary_for_chunk(chunk)
                complete_summary += summary + "\n\n"

            st.session_state.summary = complete_summary
            st.success("Complete summary generated.")
            st.write(complete_summary)

            # Generate Q&A pairs
            qna_pairs = generate_questions_and_answers(complete_summary)
            if qna_pairs:
                st.success("Q&A pairs generated.")
                for q, a in qna_pairs:
                    st.write(f"**Q:** {q}  \n**A:** {a}")

                # Save to Excel
                save_qna_to_excel(qna_pairs)
                st.success("Q&A pairs saved to Excel.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
