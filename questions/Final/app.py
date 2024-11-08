import streamlit as st
from extraction import get_chunks_from_qdrant
from mcq_generator import generate_mcqs
from qa_generator import generate_questions
from store_data import store_mcqs, store_qa

st.title("Content Generator")

collection_name = st.text_input("Enter the Qdrant collection name:")

# Create tabs for MCQ and Q&A Generation
tab_mcq, tab_qa = st.tabs(["Generate MCQs", "Generate Q&A Pairs"])

with tab_mcq:
    if st.button("Generate MCQs"):
        text_chunks = get_chunks_from_qdrant(collection_name)

        if not text_chunks:
            st.error("No chunks retrieved from Qdrant. Please check the collection name or data.")
        else:
            all_mcqs = []
            with st.spinner("Generating MCQs..."):
                for chunk in text_chunks:
                    mcqs_raw = generate_mcqs(chunk)
                    if mcqs_raw:
                        mcqs_list = mcqs_raw.split('\n')  # Adjust based on the response format
                        store_mcqs(mcqs_list)
                        st.success("MCQs generated and stored in the database.")
                    else:
                        st.warning("Failed to generate MCQs for a chunk.")

with tab_qa:
    if st.button("Generate Q&A Pairs"):
        text_chunks = get_chunks_from_qdrant(collection_name)

        if not text_chunks:
            st.error("No chunks retrieved from Qdrant. Please check the collection name or data.")
        else:
            all_qa_pairs = []
            with st.spinner("Generating Q&A pairs..."):
                for chunk in text_chunks:
                    qa_pairs_raw = generate_questions(chunk)
                    if qa_pairs_raw:
                        qa_pairs_list = qa_pairs_raw.split('\n')  # Adjust based on the response format
                        store_qa(qa_pairs_list)
                        st.success("Q&A pairs generated and stored in the database.")
                    else:
                        st.warning("Failed to generate Q&A pairs for a chunk.")
