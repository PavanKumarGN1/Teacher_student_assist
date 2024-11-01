import streamlit as st
from extraction import get_chunks_from_qdrant
from generating import generate_mcqs

# Streamlit UI
st.title("MCQ Generator from Qdrant Chunks")
collection_name = st.text_input("Enter the Qdrant collection name:", value="document_embeddings")

if st.button("Generate MCQs"):
    st.write("Retrieving text chunks from Qdrant...")
    text_chunks = get_chunks_from_qdrant(collection_name)

    if not text_chunks:
        st.error("No chunks retrieved from Qdrant. Please check the collection name or data.")
    else:
        all_mcqs = ""
        with st.spinner("Generating MCQs..."):
            for i, chunk in enumerate(text_chunks, start=1):
                mcqs = generate_mcqs(chunk)
                if mcqs:
                    st.markdown(f"### MCQs for Chunk {i}")
                    st.write(mcqs)
                    all_mcqs += mcqs + "\n\n"
                else:
                    st.warning(f"Failed to generate MCQs for Chunk {i}")

        st.success("MCQ generation completed!")
        st.download_button("Download MCQs", data=all_mcqs, file_name="mcqs.txt", mime="text/plain")
