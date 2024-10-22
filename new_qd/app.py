# import streamlit as st
# import os
# from ingest import ingest  # Import the ingest function
# from retrival import retrieve  # Import the retrieval function

# st.title("PDF Document Ingestion and Retrieval")

# # Step 1: Ingest PDF
# st.subheader("Ingest PDF Document")
# uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
# collection_name = st.text_input("Enter the collection name:")

# if st.button("Ingest PDF"):
#     if uploaded_file is not None and collection_name:
#         pdf_file_path = f"temp/{uploaded_file.name}"
#         with open(pdf_file_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         try:
#             ingest(pdf_file_path, collection_name)
#             st.success(f"PDF ingested into collection '{collection_name}' successfully.")
#         except Exception as e:
#             st.error(f"Error during ingestion: {str(e)}")
#     else:
#         st.warning("Please upload a PDF file and specify a collection name.")

# # Step 2: Retrieve Information
# st.subheader("Retrieve Information")
# user_query = st.text_input("Enter your question:")

# if st.button("Retrieve"):
#     if user_query and collection_name:
#         response = retrieve(user_query, collection_name)
#         if response:
#             st.write("Response from Llama model:")
#             st.write(response)
#         else:
#             st.warning("No relevant response found.")
#     else:
#         st.warning("Please enter a question and specify a collection name.")






######################## for multiple files ###############################

# app.py
import streamlit as st
import os
from ingest import ingest  # Import the ingest function
from retrival import retrieve  # Import the retrieve function

st.title("Multiple PDF Document Ingestion and Retrieval")

# Step 1: Ingest PDFs
st.subheader("Ingest PDF Documents")
uploaded_files = st.file_uploader("Upload multiple PDF files", type=["pdf"], accept_multiple_files=True)
collection_name = st.text_input("Enter the collection name:")

if st.button("Ingest PDFs"):
    if uploaded_files and collection_name:
        pdf_file_paths = []
        for uploaded_file in uploaded_files:
            pdf_file_path = f"temp/{uploaded_file.name}"
            with open(pdf_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            pdf_file_paths.append(pdf_file_path)

        try:
            ingest(pdf_file_paths, collection_name)
            st.success(f"PDFs ingested into collection '{collection_name}' successfully.")
        except Exception as e:
            st.error(f"Error during ingestion: {str(e)}")
    else:
        st.warning("Please upload PDF files and specify a collection name.")

# Step 2: Retrieve Information
st.subheader("Retrieve Information")
user_query = st.text_input("Enter your question:")

if st.button("Retrieve"):
    if user_query and collection_name:
        response = retrieve(user_query, collection_name)
        if response:
            st.write("Response from Llama model:")
            st.write(response)
        else:
            st.warning("No relevant response found.")
    else:
        st.warning("Please enter a question and specify a collection name.")
