import streamlit as st
import os
from ingest import store_text_in_qdrant  # Import the ingest function
from retrival import retrieve  # Import the retrieval function

# Set the title of the app
st.title("📄 PDF Document Ingestion and Retrieval")

# Sidebar for PDF ingestion
st.sidebar.header("Ingest PDF Document")
uploaded_files = st.sidebar.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
collection_name = st.sidebar.text_input("Enter the collection name:")

# Ingest PDFs into Qdrant
if st.sidebar.button("Ingest PDF"):
    if uploaded_files and collection_name:
        os.makedirs("temp", exist_ok=True)
        for uploaded_file in uploaded_files:
            pdf_file_path = f"temp/{uploaded_file.name}"
            with open(pdf_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                store_text_in_qdrant(pdf_file_path, collection_name)
                st.success(f"✅ PDF '{uploaded_file.name}' ingested into collection '{collection_name}' successfully.")
            except Exception as e:
                st.error(f"❌ Error during ingestion of '{uploaded_file.name}': {str(e)}")
    else:
        st.warning("⚠️ Please upload PDF files and specify a collection name.")

# Function to handle user input submission and response
def submit_query(user_input):
    if user_input:
        # Display user's query
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.markdown(f"<div style='text-align: left;'><b style='color: red;'>You  👤:</b> {user_input.upper()}</div>", unsafe_allow_html=True)

        if collection_name:
            # Retrieve the response for the current query
            response, references = retrieve(user_input, collection_name)
            if response:
                st.session_state.chat_history.append({"role": "ai", "content": response})
                # Display AI response
                st.markdown(f"<div style='text-align: left;'><b style='color: green;'>AI 🤖:</b> {response}</div>", unsafe_allow_html=True)

                # Display references in a structured format
                if isinstance(references, dict) and references:
                    st.markdown("<div style='text-align: left;'><b style='color: blue;'>References:</b></div>", unsafe_allow_html=True)
                    for doc_name, pages in references.items():
                        st.markdown(f"- **Document**: {doc_name} | **Pages**: {', '.join(map(str, pages))}", unsafe_allow_html=True)
                else:
                    st.warning("🔍 No references found.")
            else:
                st.warning("🔍 No relevant response found.")
        else:
            st.warning("⚠️ Please specify a collection name.")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Render chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"<div style='text-align: right;'><b style='color: red;'>You  👤:</b> {message['content'].upper()}</div>", unsafe_allow_html=True)
    elif message["role"] == "ai":
        st.markdown(f"<div style='text-align: left;'><b style='color: green;'>AI 🤖:</b> {message['content']}</div>", unsafe_allow_html=True)

# Text input bar for user query
if prompt := st.chat_input("💬 Ask your question about the uploaded PDFs here..."):
    submit_query(prompt)

# Style to keep input at bottom and hide footer
st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)
