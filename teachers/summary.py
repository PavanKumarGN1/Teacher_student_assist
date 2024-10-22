import requests
import json
import fitz  # PyMuPDF for handling PDFs

# API endpoint and headers for LLM
API_URL = 'https://rag-llm-api.accubits.cloud/v1/chat/completions'
HEADERS = {
    'api-key': 'budserve_2T9wfwNiiALTt7UAQZCoGuLPAUUTZras9cLUpYZ1',
    'Content-Type': 'application/json'
}

# Function to upload and extract text from a PDF document
def upload_document(file_path):
    try:
        with fitz.open(file_path) as pdf_document:
            document_content = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                document_content += page.get_text()

        print("Document uploaded and text extracted successfully.")
        return document_content
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None
    except Exception as e:
        print(f"An error occurred while processing the document: {str(e)}")
        return None

# Function to split the document content into smaller chunks
def split_document_content(document_content, chunk_size=5000):
    # Split the document into chunks that fit within the LLM's context window
    words = document_content.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk)
    
    return chunks

# Function to generate a summary for each chunk using the LLM
def generate_summary(document_chunk):
    data = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 100,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "This is a chat between a user and an artificial intelligence assistant"
            },
            {
                "role": "user",
                "content": f"Summarize the following document content: {document_chunk}"
            }
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return summary
    else:
        print("Failed to generate summary:", response.text)
        return None

# Function to generate teaching resources based on the summary
def generate_resources(summary):
    data = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 100,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "This is a chat between a user and an artificial intelligence assistant"
            },
            {
                "role": "user",
                "content": f"Based on the following summary, create a teaching guide, timetable, and topic planning: {summary}"
            }
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        resources = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        print("Resources generated successfully.")
        return resources
    else:
        print("Failed to generate resources:", response.text)
        return None

# Main function to run the workflow
def teacher_workflow(file_path):
    # Step 1: Document upload and text extraction
    document_content = upload_document(file_path)
    if document_content is None:
        return

    # Step 2: Split the document content into smaller chunks
    chunks = split_document_content(document_content)

    # Step 3: Generate summary for each chunk and combine summaries
    complete_summary = ""
    for i, chunk in enumerate(chunks):
        print(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
        summary = generate_summary(chunk)
        if summary is None:
            return
        complete_summary += summary + "\n"
    
    print("Generated Complete Summary:", complete_summary)

    # Step 4: Generate resources based on the combined summary
    resources = generate_resources(complete_summary)
    if resources is None:
        return
    print("Generated Resources:", resources)


# Example Usage: Replace 'sample_document.pdf' with the actual document path
if __name__ == "__main__":
    file_path = r"D:\VS_Code\teacher_student_assist\teachers\jesc101.pdf"  # Replace with the actual path to your PDF
    teacher_workflow(file_path)