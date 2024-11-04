import requests
import json
import os
import time

# Replace with your actual API key
api_key = "budserve_AorbBLLqy97G7dwGiPH5TDvqvkanMaUCybE8GrHu"

def generate_questions(text_chunk, num_questions=5):
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
                "content": "You are an AI assistant designed to create questions and answers from the provided text."
            },
            {
                "role": "user",
                "content": f"Here is the text: {text_chunk}. Create {num_questions} questions and provide answers for each."
            }
        ]
    }

    print(f"Sending chunk to model: {text_chunk[:500]}...")  # Print first 500 characters for checking
    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        response_json = response.json()
        questions_and_answers = response_json['choices'][0]['message']['content']
        end_time = time.time()
        print(f"Time taken to generate questions and answers: {end_time - start_time:.2f} seconds")
        return questions_and_answers.strip()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response text: {response.text}")
        return None
    except KeyError as e:
        print(f"Key error: {e}")
        print(f"Response structure: {response_json}")
        return None
