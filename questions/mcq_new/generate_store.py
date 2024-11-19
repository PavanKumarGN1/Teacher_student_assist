import os
import time
import json
import requests
from pymongo import MongoClient

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI") or "mongodb://127.0.0.1:27017/"
COLLECTION_NAME = "mcqs"

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client["mcq_database"]
collection = db[COLLECTION_NAME]

# Function to parse MCQs into the desired format
def parse_mcqs(raw_mcqs):
    parsed_mcqs = []
    current_question = None

    for line in raw_mcqs:
        line = line.strip()
        if line.startswith("Question"):
            if current_question:
                parsed_mcqs.append(current_question)
            current_question = {"question": line, "options": []}
        elif line.startswith(("A)", "B)", "C)", "D)")):
            if current_question:
                current_question["options"].append(line)
        elif line.startswith("Correct answer:") and current_question:
            current_question["correct_answer"] = line.replace("Correct answer:", "").strip()
            parsed_mcqs.append(current_question)
            current_question = None

    if current_question:  # Add the last question if not already added
        parsed_mcqs.append(current_question)

    return parsed_mcqs

# Function to generate MCQs and store them in MongoDB
def generate_mcqs(text_chunk, chunk_index, num_questions=5):
    url = 'https://rag-llm-api.accubits.cloud/v1/chat/completions'
    headers = {
        'api-key': os.getenv("llama_api_key") or 'your_api_key_here',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 500,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant designed to create multiple-choice questions (MCQs) from the provided text."
            },
            {
                "role": "user",
                "content": f"Here is the text: {text_chunk}. Create {num_questions} multiple-choice questions with options and mark the correct answer clearly."
            }
        ]
    }

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors

        response_json = response.json()
        raw_mcqs = response_json['choices'][0]['message']['content'].strip().split('\n')
        end_time = time.time()

        print(f"Time taken to generate MCQs: {end_time - start_time:.2f} seconds")

        # Parse the raw MCQs into the desired format
        mcq_list = parse_mcqs(raw_mcqs)

        # Insert each MCQ as a separate document into MongoDB
        for i, mcq in enumerate(mcq_list, 1):
            mcq_document = {
                "chunk_index": chunk_index,
                **mcq
            }
            collection.insert_one(mcq_document)
            print(f"MCQ {i} stored in MongoDB for chunk {chunk_index}")

        return mcq_list
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing response: {e}")
        print(f"Response text: {response.text}")
        return None
