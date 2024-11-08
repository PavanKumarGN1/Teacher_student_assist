import streamlit as st
from extraction import get_chunks_from_qdrant
from generating import generate_mcqs, format_mcqs
from store_mcqs import store_mcqs

# Streamlit UI
st.title("MCQ Generator from Qdrant Chunks")

# Sidebar for user inputs
with st.sidebar:
    st.header("MCQ Generator Settings")
    collection_name = st.text_input("Enter the Qdrant collection name:", value="data")
    output_format = st.selectbox("Select output format:", options=["json", "yaml"])

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
                    formatted_mcqs = format_mcqs(mcqs_raw, output_format=output_format)
                    if formatted_mcqs:
                        all_mcqs.append(formatted_mcqs)
                        st.markdown(f"### MCQs for Chunk {i}")
                        st.code(formatted_mcqs, language=output_format)
                else:
                    st.warning(f"Failed to generate MCQs for Chunk {i}")

        if all_mcqs:
            store_mcqs(all_mcqs, output_format)
            st.success("MCQ generation and storage completed!")
