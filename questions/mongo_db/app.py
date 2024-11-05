# ##########  only for mongodb ###########

# import streamlit as st
# from mcq_backend import main, query_vector_store
# from llm_evaluator import evaluate_answer

# # Streamlit app title
# st.title("MCQ Application")

# # Input fields for database name and collection name in the sidebar
# st.sidebar.title("Configuration")
# db_name = st.sidebar.text_input("Database Name:")
# collection_name = st.sidebar.text_input("Collection Name:")

# # Initialize the backend if database and collection names are provided
# if db_name and collection_name:
#     model, vector_store = main(db_name, collection_name)

#     # Session state to track question index
#     if 'current_index' not in st.session_state:
#         st.session_state.current_index = 0

#     # Display the current MCQ
#     def display_mcq(index):
#         if index < len(vector_store):
#             vector, options, correct_answer, doc = vector_store[index]
            
#             # Display question in bold
#             st.markdown(f"**Question {index + 1}: {doc['question']}**")

#             selected_option = st.radio("Select an option:", options)

#             # Create two columns for Submit and Next buttons
#             col1, col2 = st.columns(2)

#             # Place Submit button in the first column and Next button in the second
#             with col1:
#                 if st.button("Submit Answer"):
#                     result = evaluate_answer(selected_option, correct_answer)
#                     st.write(result)

#             with col2:
#                 if st.button("Next Question"):
#                     st.session_state.current_index += 1

#         else:
#             st.write("No more questions available.")

#     # Display the current question
#     display_mcq(st.session_state.current_index)















################ For application ###############


# mongo_db/app.py

import streamlit as st
from .mcq_backend import main as initialize_backend, query_vector_store
from .llm_evaluator import evaluate_answer


def main():
    # Streamlit app title
    #st.title("MCQ Application")

    # Input fields for database name and collection name in the sidebar
    st.sidebar.title("Configuration")
    db_name = st.sidebar.text_input("Database Name:")
    collection_name = st.sidebar.text_input("Collection Name:")

    # Initialize the backend if database and collection names are provided
    if db_name and collection_name:
        model, vector_store = initialize_backend(db_name, collection_name)

        # Session state to track question index
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0

        # Display the current MCQ
        def display_mcq(index):
            if index < len(vector_store):
                vector, options, correct_answer, doc = vector_store[index]
                
                # Display question in bold
                st.markdown(f"**Question {index + 1}: {doc['question']}**")

                selected_option = st.radio("Select an option:", options)

                # Create two columns for Submit and Next buttons
                col1, col2 = st.columns(2)

                # Place Submit button in the first column and Next button in the second
                with col1:
                    if st.button("Submit Answer"):
                        result = evaluate_answer(selected_option, correct_answer)
                        st.write(result)

                with col2:
                    if st.button("Next Question"):
                        st.session_state.current_index += 1

            else:
                st.write("No more questions available.")

        # Display the current question
        display_mcq(st.session_state.current_index)
