import os
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# Initialize Qdrant client with environment variables
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    port=6333,
    timeout=120
)

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

# Store text chunks and embeddings into Qdrant
def store_text_in_qdrant(pdf_file_path, collection_name="text_chunks", batch_size=10):
    if not os.path.exists(pdf_file_path):
        raise FileNotFoundError(f"The file {pdf_file_path} does not exist.")

    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    text_data = extract_text_from_pdf(pdf_file_path)
    chunks = split_text_into_smaller_chunks(text_data, max_chunk_length=500)
    
    logging.info(f"Text split into {len(chunks)} chunks from {pdf_file_path}")

    embeddings = model.encode([chunk[1] for chunk in chunks])  # Encode only the text part
    logging.info(f"Generated {len(embeddings)} embeddings from {pdf_file_path}")

    # Check if collection exists and create if not
    if collection_name not in [col.name for col in qdrant_client.get_collections().collections]:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE)
        )
        logging.info(f"Collection '{collection_name}' created")

    # Create points with embeddings and metadata (document name and page)
    points = [
        PointStruct(
            id=i,
            vector=vector.tolist(),
            payload={
                "text": chunks[i][1],  # The chunk text
                "document": os.path.basename(pdf_file_path),  # Add document name
                "page": chunks[i][0]  # Add page number
            }
        )
        for i, vector in enumerate(embeddings)
    ]
    
    logging.info(f"Created {len(points)} points for upsert")

    # Upsert points in batches
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        qdrant_client.upsert(collection_name=collection_name, points=batch)
        logging.info(f"Upserted batch {i // batch_size + 1} of {len(points) // batch_size + 1}")
