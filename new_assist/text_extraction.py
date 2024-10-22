import os
import logging
from PyPDF2 import PdfReader

# Initialize logger
logging.basicConfig(level=logging.INFO)

# Text extraction function from PDFs
def extract_text_from_pdf(pdf_file_path):
    reader = PdfReader(pdf_file_path)
    text_data = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:  # Check if text extraction was successful
            text_data.append((page_num + 1, text))  # Page number starts from 1
    return text_data

# Split text into smaller chunks for embedding
def split_text_into_smaller_chunks(text_data, max_chunk_length=500):
    chunks = []
    for page_num, page_text in text_data:
        for i in range(0, len(page_text), max_chunk_length):
            chunk = page_text[i:i + max_chunk_length]
            chunks.append((page_num, chunk))
    return chunks
