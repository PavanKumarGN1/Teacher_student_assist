import streamlit as st
from extraction import get_chunks_from_qdrant
from generating import generate_questions
from store_questions import store_questions  # Import the MongoDB handler

# Streamlit UI
st.title("Q&A Generator from Qdrant Chunks")

# Sidebar for user inputs
with st.sidebar:
    st.header("Q&A Generator from Qdrant Chunks")
    collection_name = st.text_input("Enter the Qdrant collection name:", value="data")

# Button to generate Q&A
if st.button("Generate Q&A"):
    st.write("Retrieving text chunks from Qdrant...")
    text_chunks = get_chunks_from_qdrant(collection_name)

    if not text_chunks:
        st.error("No chunks retrieved from Qdrant. Please check the collection name or data.")
    else:
        all_questions_and_answers = []
        with st.spinner("Generating Questions and Answers..."):
            for i, chunk in enumerate(text_chunks, start=1):
                qa_raw = generate_questions(chunk)
                if qa_raw:
                    # Process raw Q&A pairs into structured format
                    qa_list = []
                    # Assuming the raw output comes in a structured format, we'll parse it correctly.
                    for qa_block in qa_raw.strip().split("\n\n"):
                        lines = qa_block.strip().split("\n")
                        if len(lines) >= 2:  # Ensure there are enough lines for a Q&A pair
                            question = lines[0]
                            answer = lines[1]  # Assuming the answer follows the question
                            qa_list.append({
                                "question": question,
                                "answer": answer
                            })
                    all_questions_and_answers.extend(qa_list)  # Add to the overall list

                    # Display Q&A pairs on the Streamlit app
                    st.markdown(f"### Questions and Answers for Chunk {i}")
                    for qa in qa_list:
                        st.markdown(f"**Question:** {qa['question']}")
                        st.markdown(f"**Answer:** {qa['answer']}")

                else:
                    st.warning(f"Failed to generate Q&A pairs for Chunk {i}")

        # Store Q&A pairs in MongoDB
        if all_questions_and_answers:
            store_questions(all_questions_and_answers)
        
        st.success("Q&A generation and storage completed!")
