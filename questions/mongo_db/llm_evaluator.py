import os
from budserve.models.langchain import BudServeClient
import streamlit as st

# Load the language model
api_key = os.getenv('llama_api_key')
llm = BudServeClient(base_url="https://rag-llm-api.accubits.cloud/v1",
                     model_name="meta-llama/Meta-Llama-3-8B-Instruct",
                     api_key=api_key,
                     max_tokens=500)

def evaluate_answer(user_answer, correct_answer_text):
    # Remove any identifier (e.g., "B) ") from correct answer text
    correct_answer_text = correct_answer_text.split(")", 1)[-1].strip()
    
    # Debugging: Print user answer and cleaned correct answer for verification
    print(f"User Answer (raw): '{user_answer}', Correct Answer (cleaned): '{correct_answer_text}'")

    # Normalize the answers for comparison
    user_answer_normalized = user_answer.strip().lower()
    correct_answer_normalized = correct_answer_text.strip().lower()

    # Debugging: Print normalized values
    print(f"User Answer (normalized): '{user_answer_normalized}', Correct Answer (normalized): '{correct_answer_normalized}'")

    # Compare the normalized answers
    if user_answer_normalized == correct_answer_normalized:
        st.success(" Correct Answer! 🎉")
    else:
        st.error(f"❌ Wrong Answer! The correct answer is: **{correct_answer_text}**")

