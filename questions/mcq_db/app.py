# # questions/mcq_db/app.py

import streamlit as st
from extraction import get_chunks_from_qdrant
from generating import generate_mcqs
from store_mcqs import store_mcqs  # Import the MongoDB handler

# Streamlit UI
st.title("MCQ Generator from Qdrant Chunks")

# Sidebar for user inputs
with st.sidebar:
    st.header("MCQ Generator from Qdrant Chunks")
    collection_name = st.text_input("Enter the Qdrant collection name:", value="data")

# Button to generate MCQs
if st.button("Generate MCQs"):
    st.write("Retrieving text chunks from Qdrant...")
    text_chunks = get_chunks_from_qdrant(collection_name)

    if not text_chunks:
        st.error("No chunks retrieved from Qdrant. Please check the collection name or data.")
    else:
        all_mcqs = []
        with st.spinner("Generating MCQs..."):
            for i, chunk in enumerate(text_chunks, start=1):
                mcqs_raw = generate_mcqs(chunk)
                if mcqs_raw:
                    # Process raw MCQs into structured format
                    mcq_list = []
                    # Assuming the raw MCQs come as a structured format, we'll split them correctly.
                    for question_block in mcqs_raw.strip().split("\n\n"):
                        lines = question_block.strip().split("\n")
                        if len(lines) >= 5:  # Ensure there are enough lines for a question
                            question = lines[0]
                            options = lines[1:5]  # Next four lines are options
                            correct_answer = lines[5] if len(lines) > 5 else ""  # Ensure this line exists
                            mcq_list.append({
                                "question": question,
                                "options": options,
                                "correct_answer": correct_answer
                            })
                    all_mcqs.extend(mcq_list)  # Add to the overall list

                    # Display MCQs on the Streamlit app
                    st.markdown(f"### MCQs for Chunk {i}")
                    for mcq in mcq_list:
                        st.markdown(f"**Question:** {mcq['question']}")
                        for option in mcq['options']:
                            st.markdown(f"- {option}")
                        st.markdown(f"**Correct Answer:** {mcq['correct_answer']}")

                else:
                    st.warning(f"Failed to generate MCQs for Chunk {i}")

        # Store MCQs in MongoDB
        if all_mcqs:
            store_mcqs(all_mcqs)
        
        st.success("MCQ generation and storage completed!")

