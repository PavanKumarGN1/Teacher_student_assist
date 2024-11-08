## Generating.py

import requests
import json
import os
import time

api_key = os.getenv("llama_api_key") or 'your_api_key_here'

def generate_mcqs(text_chunk, num_questions=5):
    url = 'https://rag-llm-api.accubits.cloud/v1/chat/completions'
    headers = {
        'api-key': api_key,
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
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        response_json = response.json()
        mcqs = response_json['choices'][0]['message']['content']
        end_time = time.time()
        print(f"Time taken to generate MCQs: {end_time - start_time:.2f} seconds")
        return mcqs.strip()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing response: {e}")
        print(f"Response text: {response.text}")
        return None


