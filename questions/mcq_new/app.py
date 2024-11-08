# ## app.py 

# import streamlit as st
# from extraction import get_chunks_from_qdrant
# from generating import generate_mcqs
# from store_mcqs import store_mcqs
# import json

# # Streamlit UI
# st.title("MCQ Generator from Qdrant Chunks")

# # Sidebar for user inputs
# with st.sidebar:
#     st.header("MCQ Generator Settings")
#     collection_name = st.text_input("Enter the Qdrant collection name:", value="document_embeddings")
#     num_questions = st.number_input("Number of MCQs per chunk", min_value=1, max_value=10, value=5)

# # Button to generate and store MCQs
# if st.button("Generate and Store MCQs"):
#     st.write("Retrieving text chunks from Qdrant...")
#     text_chunks = get_chunks_from_qdrant(collection_name)

#     if not text_chunks:
#         st.error("No chunks retrieved from Qdrant. Please check the collection name or data.")
#     else:
#         all_mcqs = []
#         with st.spinner("Generating MCQs..."):
#             for chunk in text_chunks:
#                 mcqs_raw = generate_mcqs(chunk, num_questions=num_questions)
#                 if mcqs_raw:
#                     all_mcqs.append(mcqs_raw)
#                     st.write(mcqs_raw)
#                 else:
#                     st.warning("Failed to generate MCQs for a chunk")

#         if all_mcqs:
#             st.write("Storing generated MCQs in MongoDB...")
#             store_mcqs(json.dumps(all_mcqs))
#             st.success("MCQ generation and storage completed!")





import streamlit as st
from extraction import get_chunks_from_qdrant
from generating import generate_mcqs
from store_mcqs import store_mcqs
import json

# Streamlit UI
st.title("MCQ Generator from Qdrant Chunks")

# Sidebar for user inputs
with st.sidebar:
    st.header("MCQ Generator Settings")
    collection_name = st.text_input("Enter the Qdrant collection name:", value="document_embeddings")
    num_questions = st.number_input("Number of MCQs per chunk", min_value=1, max_value=10, value=5)

# Button to generate and store MCQs
if st.button("Generate and Store MCQs"):
    st.write("Retrieving text chunks from Qdrant...")
    text_chunks = get_chunks_from_qdrant(collection_name)

    if not text_chunks:
        st.error("No chunks retrieved from Qdrant. Please check the collection name or data.")
    else:
        all_mcqs = []
        with st.spinner("Generating MCQs..."):
            for idx, chunk in enumerate(text_chunks):
                try:
                    # Generate MCQs for the current chunk
                    mcqs = generate_mcqs(chunk, num_questions=num_questions)

                    # Log the raw response for debugging
                    st.write(f"Raw MCQ Response for chunk {idx + 1}: {mcqs}")
                    
                    # Check if the response is a valid JSON string
                    if isinstance(mcqs, str):
                        try:
                            mcqs = json.loads(mcqs)
                        except json.JSONDecodeError:
                            st.error(f"Failed to parse MCQs for chunk {idx + 1}. Response was not JSON.")
                            continue  # Skip this chunk and move to the next one

                    # Validate and display each MCQ
                    if mcqs and isinstance(mcqs, list):
                        for mcq in mcqs:
                            # Ensure each MCQ has the expected fields
                            if isinstance(mcq, dict) and 'question' in mcq and 'options' in mcq and 'correct_answer' in mcq:
                                all_mcqs.append(mcq)  # Append to main list for storage

                                # Display MCQ details on Streamlit
                                st.write(f"Question: {mcq['question']}")
                                for i, option in enumerate(mcq['options'], 1):
                                    st.write(f"{i}. {option}")
                                st.write(f"Correct Answer: {mcq['correct_answer']}")
                            else:
                                st.warning(f"Incomplete MCQ structure in chunk {idx + 1}. Skipping this MCQ.")
                    else:
                        st.warning(f"Failed to generate valid MCQs for chunk {idx + 1}.")
                except Exception as e:
                    st.error(f"An error occurred while generating MCQs for chunk {idx + 1}: {e}")

        # Store all valid MCQs
        if all_mcqs:
            st.write("Storing generated MCQs in MongoDB...")
            store_mcqs(all_mcqs)
            st.success("MCQ generation and storage completed!")
        else:
            st.error("No valid MCQs were generated to store in MongoDB.")

