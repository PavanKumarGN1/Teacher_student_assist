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
#             for idx, chunk in enumerate(text_chunks):
#                 try:
#                     # Generate MCQs for the current chunk
#                     mcqs_response = generate_mcqs(chunk, num_questions=num_questions)

#                     # Log raw response for debugging
#                     st.write(f"Raw MCQ Response for chunk {idx + 1}: {mcqs_response}")

#                     # Ensure response is a string and attempt to parse it as JSON
#                     if isinstance(mcqs_response, str):
#                         try:
#                             mcqs_response = json.loads(mcqs_response)
#                         except json.JSONDecodeError as e:
#                             st.error(f"Failed to parse response for chunk {idx + 1}: {e}")
#                             continue  # Skip this chunk and move to the next one

#                     # Validate MCQ structure and append valid ones
#                     if isinstance(mcqs_response, list):
#                         for mcq in mcqs_response:
#                             if isinstance(mcq, dict) and 'question' in mcq and 'options' in mcq and 'correct_answer' in mcq:
#                                 all_mcqs.append(mcq)
#                                 # Display each MCQ
#                                 st.write(f"Question: {mcq['question']}")
#                                 for i, option in enumerate(mcq['options'], 1):
#                                     st.write(f"{i}. {option}")
#                                 st.write(f"Correct Answer: {mcq['correct_answer']}")
#                             else:
#                                 st.warning(f"Invalid MCQ structure in chunk {idx + 1}. Skipping.")
#                     else:
#                         st.warning(f"No valid MCQs generated for chunk {idx + 1}.")
#                 except Exception as e:
#                     st.error(f"Error generating MCQs for chunk {idx + 1}: {e}")

#         # Store all valid MCQs
#         if all_mcqs:
#             st.write("Storing generated MCQs in MongoDB...")
#             try:
#                 store_mcqs(all_mcqs)
#                 st.success("MCQ generation and storage completed!")
#             except Exception as e:
#                 st.error(f"Failed to store MCQs in MongoDB: {e}")
#         else:
#             st.error("No valid MCQs were generated to store in MongoDB.")


# import streamlit as st
# from extraction import get_chunks_from_qdrant
# from generating import generate_mcqs

# # Streamlit UI
# st.title("MCQ Generator from Qdrant Chunks")

# # Input fields for Qdrant collection name and number of MCQs
# collection_name = st.sidebar.text_input("Enter the Qdrant collection name:", "document_embeddings")
# num_mcqs = st.sidebar.number_input("Number of MCQs per chunk:", min_value=1, max_value=10, value=5)

# if st.button("Generate MCQs"):
#     st.write("Retrieving text chunks from Qdrant...")
    
#     # Retrieve chunks from Qdrant
#     chunks = get_chunks_from_qdrant(collection_name)
    
#     if not chunks:
#         st.error("No text chunks retrieved from Qdrant.")
#     else:
#         st.write("Generating MCQs...")
#         mcq_results = []

#         for i, chunk in enumerate(chunks):
#             st.write(f"Processing chunk {i + 1}...")
#             mcqs = generate_mcqs(chunk, num_questions=num_mcqs)

#             if mcqs:
#                 st.write(f"Generated MCQs for chunk {i + 1}:")
#                 st.write(mcqs)
#                 mcq_results.append(mcqs)
#             else:
#                 st.warning(f"No valid MCQs generated for chunk {i + 1}.")

#         if mcq_results:
#             st.success("MCQs generation completed.")
#         else:
#             st.error("No MCQs generated for any chunks.")

    



import streamlit as st
from extraction import get_chunks_from_qdrant
from generating import generate_mcqs

st.title("MCQ Generator and MongoDB Storage")



Credentials = st.sidebar.title("Credentials :")
# Input fields for Qdrant collection name and number of MCQs

collection_name = st.sidebar.text_input("Enter the Qdrant collection name:", "document_embeddings")
num_mcqs = st.sidebar.number_input("Number of MCQs per chunk:", min_value=1, max_value=10, value=5)

if st.button("Generate MCQs"):
    st.write("Retrieving text chunks from Qdrant...")
    
    # Retrieve chunks from Qdrant
    chunks = get_chunks_from_qdrant(collection_name)
    
    if not chunks:
        st.error("No text chunks retrieved from Qdrant.")
    else:
        st.write("Generating MCQs and storing them in MongoDB...")
        for i, chunk in enumerate(chunks):
            st.write(f"Processing chunk {i + 1}...")
            mcqs = generate_mcqs(chunk, chunk_index=i + 1, num_questions=num_mcqs)

            if mcqs:
                st.write(f"Generated MCQs for chunk {i + 1}:")
                st.write(mcqs)
            else:
                st.warning(f"No valid MCQs generated for chunk {i + 1}.")
        
        st.success("MCQ generation and storage completed.")
