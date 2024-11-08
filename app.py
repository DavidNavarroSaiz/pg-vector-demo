# streamlit_app.py

import streamlit as st
from src.db.db_manager import DatabaseManager
from src.document_processor import process_and_store_document
from src.document_retriever import search_documents
import os
import re

# Initialize database manager
db_manager = DatabaseManager()

# Fetch options for dropdowns
sections = db_manager.get_sections()
subsections = db_manager.get_subsections()
categories = db_manager.get_categories()
learning_types = db_manager.get_learning_types()
permissions = db_manager.get_permissions()

# Set up two tabs
tab1, tab2 = st.tabs(["Upload Document", "Get Recommendations"])

# Upload Document tab
with tab1:
    st.header("Upload and Process Document")

    uploaded_file = st.file_uploader("Upload a Document", type=["pdf", "docx", "txt", "pptx", "mp4", "jpg", "jpeg", "png"])
    youtube_url = st.text_input("Or enter a YouTube URL")

    # Regular expression to validate YouTube URL
    youtube_regex = re.compile(
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    # Dropdowns for metadata fields
    selected_section = st.selectbox("Select Section", list(sections.keys()))
    selected_subsection = st.selectbox("Select Subsection", list(subsections.keys()))
    selected_category = st.selectbox("Select Category", list(categories.keys()))
    selected_learning_type = st.selectbox("Select Learning Type", list(learning_types.keys()))
    selected_permission = st.selectbox("Select Permission", permissions)

    # Button to upload and process the document
    if st.button("Upload and Process Document"):
        if uploaded_file is not None or youtube_regex.match(youtube_url):
            # Save the uploaded file to a temporary path
            if uploaded_file:
                temp_dir = "temp"
                os.makedirs(temp_dir, exist_ok=True)  # Create temp directory if it doesn't exist
                doc_path = os.path.join(temp_dir, uploaded_file.name)

                with open(doc_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            elif youtube_regex.match(youtube_url):
                doc_path = youtube_url

            # Call the function with selected options and document path
            message, result = process_and_store_document(
                doc_path=doc_path,
                section_id=sections[selected_section],
                sub_section_id=subsections[selected_subsection],
                learning_type_id=learning_types[selected_learning_type],
                category_id=categories[selected_category],
                permissions_allowed=selected_permission
            )

            # Delete the temporary file if it was uploaded as a local file
            if uploaded_file and doc_path and os.path.exists(doc_path):
                os.remove(doc_path)
                print(f"Temporary file {doc_path} deleted.")

            # Display the appropriate message based on upload status
            if "successfully" in message:
                st.success(message)
                
                # Display summary and additional details
                st.subheader("Document Summary")
                st.write(result.get("summary", "No summary available"))
                
                st.subheader("Cost Details")
                st.write(f"**GPT Model Cost:** ${result.get('cost', 0):.6f}")

                # Display token details if available
                st.subheader("Token Details")
                st.write(f"**Prompt Tokens:** {result.get('prompt_tokens', 'N/A')}")
                st.write(f"**Completion Tokens:** {result.get('completion_tokens', 'N/A')}")

                # Display additional details if available
                if "resolution" in result:
                    st.subheader("Image Resolution")
                    st.write(f"{result['resolution']}")

                if "audio_duration_minutes" in result:
                    st.subheader("Audio Duration")
                    st.write(f"{result['audio_duration_minutes']} minutes")

            else:
                st.error(message)  # Display the error message if document already exists or summary wasn't generated

        else:
            st.error("Please upload a document or enter a valid YouTube URL before submitting.")

# Get Recommendations tab
with tab2:
    st.header("Get Document Recommendations")

    # Input field for search query
    search_query = st.text_input("Enter search query")

    # Slider for the number of results to display
    result_limit = st.slider("Number of results", min_value=1, max_value=10, value=5)

    # Button to perform search
    if st.button("Search"):
        if search_query:
            # Perform search using the function in document_retriever.py
            search_results = search_documents(search_query, limit=result_limit)
            
            # Display search results
            for idx, result in enumerate(search_results, 1):
                st.subheader(f"Result {idx}")
                st.write(f"**Content:** {result['content']}")
                st.write(f"**Chunk Order:** {result['chunk_order']}")
                st.write(f"**Date:** {result['date']}")
                st.write(f"**Summary:** {result['summary']}")
                st.write(f"**Metadata:** {result['metadata']}")
                st.write(f"**Resource ID:** {result['resource_id']}")
                st.write(f"**Resource Name:** {result['resource_name']}")
                st.write(f"**Path:** {result['path']}")
                st.write(f"**Permissions Allowed:** {result['permissions_allowed']}")
                st.write(f"**Category ID:** {result['category_id']}")
                st.write(f"**Subsection ID:** {result['sub_section_id']}")
                st.write(f"**Learning Type ID:** {result['learning_type_id']}")
                st.write(f"**Distance:** {result['distance']:.4f}")
                st.write("---")  # Separator between results
        else:
            st.error("Please enter a search query.")
