# import streamlit as st
# import sys
# import os

# # Add the base directory to the Python path to access other folders
# sys.path.append(os.path.abspath("D:/VS_Code/teacher_student_assist"))

# # Import the functions from the necessary modules
# from new_app.ingest import store_text_in_qdrant  # Import the ingest function
# from new_app.retrival import retrieve  # Import the retrieval function
# from new_app import app as chat_with_document_module  # Import the chat functionality module
# from questions.mongo_db import app as mcq_question_module  # Import the MCQ functionality module

# # Define the Streamlit UI layout
# st.title("Teacher Student Assist")

# # Create tabs for each functionality
# tab1, tab2 = st.tabs(["Chat with Document", "MCQ Question"])

# # Define the content for each tab
# with tab1:
#     st.header("Chat with Document")
#     chat_with_document_module.main()  # Run the main function for chat functionality

# with tab2:
#     st.header("MCQ Question")
#     mcq_question_module.main()  # Run the main function for MCQ functionality


import streamlit as st
import sys
import os

# Add the base directory to the Python path to access other folders
sys.path.append(os.path.abspath("D:/VS_Code/teacher_student_assist"))

# Import the functions from the necessary modules
from new_app.ingest import store_text_in_qdrant  # Import the ingest function
from new_app.retrival import retrieve  # Import the retrieval function
from new_app import app as chat_with_document_module  # Import the chat functionality module
from questions.mongo_db import app as mcq_question_module  # Import the MCQ functionality module

# Define the Streamlit UI layout
st.title("Teacher Student Assist")

# Create a sidebar for navigation
selected_option = st.sidebar.selectbox("Select Functionality", ["Chat with Document", "MCQ Question"])

# Define the content for each selected functionality
if selected_option == "Chat with Document":
    st.header("📄 Chat with Document")

    st.markdown("-----------------------------------------------------------------------------------------")

    chat_with_document_module.main()  # Run the main function for chat functionality
elif selected_option == "MCQ Question":
    st.header("MCQ Application :")
    mcq_question_module.main()  # Run the main function for MCQ functionality

    st.markdown("-----------------------------------------------------------------------------------------")

