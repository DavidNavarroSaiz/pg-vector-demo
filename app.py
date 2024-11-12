# streamlit_app.py

import streamlit as st
from src.db.db_manager import DatabaseManager
from src.document_processor import process_and_store_document
from src.document_retriever import search_documents
from src.langchain_processor import LangchainProcessor

import os
import re

# Initialize database manager
db_manager = DatabaseManager()
langchain_processor = LangchainProcessor()
# Fetch options for dropdowns
sections = db_manager.get_sections()
subsections = db_manager.get_subsections()
categories = db_manager.get_categories()
learning_types = db_manager.get_learning_types()
permissions = db_manager.get_permissions()
available_sources = db_manager.get_all_resource_paths()
# Set up two tabs
tab1, tab2 = st.tabs(["Upload Document", "Get Recommendations"])

# Upload Document tab
with tab1:
    st.header("Upload and Process Document")
    uploaded_file = st.file_uploader("Upload a Document", type=["pdf", "docx", "txt", "pptx", "mp4", "jpg", "jpeg", "png"])
    youtube_url = st.text_input("Or enter a YouTube URL")

    # Regular expression to validate YouTube URL
    youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

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
                os.makedirs(temp_dir, exist_ok=True)
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
                st.error(message)
        else:
            st.error("Please upload a document or enter a valid YouTube URL before submitting.")

# Get Recommendations tab
with tab2:
    st.header("Get Document Recommendations")
    # Display available sources at the top
    st.subheader("Available Sources")
    if available_sources:
        for idx, source in enumerate(available_sources, 1):
            st.write(f"{idx}. {source}")
    else:
        st.write("No sources available yet, please upload documents.")
            
    # Input field for search query
    search_query = st.text_input("Enter search query")

    # Slider for the number of results to display
    result_limit = st.slider("Number of results", min_value=1, max_value=10, value=5)

    # Optional filters
    selected_resource_id = st.number_input("Resource ID (Optional)", min_value=0, step=1)
    selected_permission_filter = st.selectbox("Permissions Allowed (Optional)", ["Any"] + permissions)
    selected_category_filter = st.selectbox("Category (Optional)", ["Any"] + list(categories.keys()))
    selected_subsection_filter = st.selectbox("Subsection (Optional)", ["Any"] + list(subsections.keys()))
    selected_learning_type_filter = st.selectbox("Learning Type (Optional)", ["Any"] + list(learning_types.keys()))

    # Prepare filters for LangchainProcessor
    langchain_filters = {}

    if selected_resource_id != 0:
        langchain_filters["resource_id"] = {"$eq": selected_resource_id}

    if selected_permission_filter != "Any":
        langchain_filters["permissions_allowed"] = {"$eq": selected_permission_filter}

    if selected_category_filter != "Any":
        langchain_filters["category_id"] = {"$eq": categories[selected_category_filter]}

    if selected_subsection_filter != "Any":
        langchain_filters["sub_section_id"] = {"$eq": subsections[selected_subsection_filter]}

    if selected_learning_type_filter != "Any":
        langchain_filters["learning_type_id"] = {"$eq": learning_types[selected_learning_type_filter]}

    # Button to perform search
    if st.button("Search"):
        if search_query:
            # Perform search using the function in document_retriever.py
            search_results = search_documents(
                search_query,
                limit=result_limit,
                resource_id=selected_resource_id if selected_resource_id != 0 else None,
                permissions_allowed=selected_permission_filter if selected_permission_filter != "Any" else None,
                category_id=categories[selected_category_filter] if selected_category_filter != "Any" else None,
                sub_section_id=subsections[selected_subsection_filter] if selected_subsection_filter != "Any" else None,
                learning_type_id=learning_types[selected_learning_type_filter] if selected_learning_type_filter != "Any" else None,
            )

            # Perform search with LangchainProcessor
            search_langchain_results = langchain_processor.similarity_search_with_scores(
                search_query,
                k=result_limit,
                filter=langchain_filters
            )

            # Display search results in two columns
            col1, col2 = st.columns(2)

            # Display DocumentRetriever results
            with col1:
                st.subheader("DocumentRetriever Results")
                if search_results:
                    for idx, result in enumerate(search_results, 1):
                        st.write(f"**Result {idx}**")
                        st.write(f"- **Content:** {result['content']}")
                        st.write(f"- **Resource Name:** {result['resource_name']}")
                        st.write(f"- **Distance:** {result['distance']:.4f}")
                        st.write("---")
                else:
                    st.write("No results found.")

            # Display LangchainProcessor results
            with col2:
                st.subheader("LangchainProcessor Results")
                if search_langchain_results:
                    for idx, (doc, score) in enumerate(search_langchain_results, 1):
                        st.write(f"**Result {idx}**")
                        st.write(f"- **Content:** {doc.page_content}")
                        st.write(f"- **Resource Name:** {doc.metadata.get('resource_name', 'N/A')}")
                        st.write(f"- **Distance:** {score:.4f}")
                        st.write("---")
                else:
                    st.write("No results found.")
        else:
            st.error("Please enter a search query.")