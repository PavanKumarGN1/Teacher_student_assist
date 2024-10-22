import fitz  # PyMuPDF for PDF processing
import os
import uuid
import numpy as np
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Pinecone configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # This should now correctly load from the .env file
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "rag"
PINECONE_HOST = "https://rag-9b59e32.svc.aped-4627-b74a.pinecone.io"
DIMENSIONS = 768  # Embedding dimension based on your requirement
METRIC = "cosine"

# Initialize Pinecone client
if not PINECONE_API_KEY:
    raise ValueError("Pinecone API Key not found. Please check your .env file.")

pc = Pinecone(api_key=PINECONE_API_KEY)

# Load the embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def chunk_text(text, chunk_size=512):
    """Split text into chunks of specified size."""
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def store_embeddings_in_pinecone(chunks):
    print("Connecting to Pinecone...")

    # Check if the index exists
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating index '{INDEX_NAME}'...")
        pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSIONS,  # Use 384 for the embedding dimension
        metric=METRIC,
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

    # Connect to the index
    index = pc.Index(INDEX_NAME)

    # Store embeddings
    for chunk in chunks:
        embedding = embedding_model.encode(chunk).tolist()
        point_id = str(uuid.uuid4())  # Unique ID for each point
        index.upsert(vectors=[(point_id, embedding, {"text": chunk})])
        print(f"Stored embedding for chunk with ID: {point_id}")

    print("Embeddings stored in Pinecone.")

if __name__ == "__main__":
    # Path to your PDF file
    pdf_path = r"D:\VS_Code\teacher_student_assist\teachers\jesc101.pdf"  # Change this to your PDF file path

    # Extract text and chunk it
    text = extract_text_from_pdf(pdf_path)
    print(f"Extracted text from {pdf_path}.")

    chunks = chunk_text(text)
    print(f"Generated {len(chunks)} chunks from the document.")

    # Store embeddings in Pinecone
    store_embeddings_in_pinecone(chunks)
