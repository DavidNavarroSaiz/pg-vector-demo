# streamlit_app.py

import streamlit as st
from src.db.db_manager import DatabaseManager
from src.document_processor import process_and_store_document
from src.document_retriever import search_documents
from src.langchain_processor import LangchainProcessor

import os
import re

# Page config
st.set_page_config(
    page_title="Document Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .stProgress .st-bo {
        background-color: #00cc00;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database manager
db_manager = DatabaseManager()
langchain_processor = LangchainProcessor()

def refresh_resources():
    """Helper function to refresh the resources list"""
    return db_manager.get_all_resource_paths()

# Initialize session state
if 'available_sources' not in st.session_state:
    st.session_state.available_sources = refresh_resources()

# Fetch options for dropdowns
sections = db_manager.get_sections()
subsections = db_manager.get_subsections()
categories = db_manager.get_categories()
learning_types = db_manager.get_learning_types()
permissions = db_manager.get_permissions()

# Main title with emoji
st.title("📚 Document Management System")

# Set up two tabs with icons
tab1, tab2 = st.tabs(["📤 Upload Document", "🔍 Get Recommendations"])

# Upload Document tab
with tab1:
    st.header("Upload and Process Document")
    
    # Create two columns for upload options
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a Document",
            type=["pdf", "docx", "txt", "pptx", "mp4", "jpg", "jpeg", "png"],
            help="Supported formats: PDF, Word, Text, PowerPoint, Video, and Images"
        )
    
    with col2:
        youtube_url = st.text_input(
            "Or enter a YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            help="Enter a valid YouTube video URL"
        )

    # Regular expression to validate YouTube URL
    youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    # Only show categorization fields if a file is uploaded or YouTube URL is entered
    if uploaded_file is not None or youtube_regex.match(youtube_url):
        st.subheader("Document Categorization")
        selected_section = st.selectbox("Section", list(sections.keys()), help="Choose the main section")
        selected_subsection = st.selectbox("Subsection", list(subsections.keys()), help="Choose a subsection")
        selected_category = st.selectbox("Category", list(categories.keys()), help="Select content category")
        selected_learning_type = st.selectbox("Learning Type", list(learning_types.keys()), help="Choose the type of learning content")
        selected_permission = st.selectbox("Permission Level", permissions, help="Set access permissions")

        # Upload button with progress indication
        if st.button("📤 Upload and Process Document", use_container_width=True):
            with st.spinner('🔄 Processing document... Please wait.'):
                progress_bar = st.progress(0)
                
                # Save the uploaded file to a temporary path
                if uploaded_file:
                    temp_dir = "temp"
                    os.makedirs(temp_dir, exist_ok=True)
                    doc_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(doc_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    progress_bar.progress(25)
                else:
                    doc_path = youtube_url
                    progress_bar.progress(25)

                # Process document
                message, result = process_and_store_document(
                    doc_path=doc_path,
                    section_id=sections[selected_section],
                    sub_section_id=subsections[selected_subsection],
                    learning_type_id=learning_types[selected_learning_type],
                    category_id=categories[selected_category],
                    permissions_allowed=selected_permission
                )
                progress_bar.progress(75)

                # Cleanup
                if uploaded_file and doc_path and os.path.exists(doc_path):
                    os.remove(doc_path)
                    # Remove the file from available sources if it exists
                    if uploaded_file.name in st.session_state.available_sources:
                        st.session_state.available_sources.remove(uploaded_file.name)
                progress_bar.progress(100)

                # Display results in an expander
                if "successfully" in message:
                    st.success(message)
                    st.session_state.available_sources = refresh_resources()
                    
                    with st.expander("📋 View Document Details", expanded=True):
                        # Summary section
                        st.markdown("### 📝 Document Summary")
                        st.info(result.get("summary", "No summary available"))
                        
                        # Create three columns for metrics
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.metric("GPT Model Cost", f"${result.get('cost', 0):.6f}")
                        
                        with metric_col2:
                            st.metric("Prompt Tokens", result.get('prompt_tokens', 'N/A'))
                        
                        with metric_col3:
                            st.metric("Completion Tokens", result.get('completion_tokens', 'N/A'))

                        # Additional details if available
                        if "resolution" in result:
                            st.info(f"📐 Image Resolution: {result['resolution']}")

                        if "audio_duration_minutes" in result:
                            st.info(f"⏱️ Duration: {result['audio_duration_minutes']} minutes")
                else:
                    st.error(message)
    else:
        st.info("⚠️ Please upload a document or enter a valid YouTube URL to proceed.")

# Get Recommendations tab
with tab2:
    st.header("Get Document Recommendations")
    # Display available sources in an expander
    with st.expander("📚 Available Sources", expanded=False):
        current_sources = st.session_state.available_sources
        if current_sources:
            for idx, source in enumerate(current_sources, 1):
                st.write(f"{idx}. {source}")
        else:
            st.info("No sources available yet. Please upload documents first.")
            
    # Create sidebar for filters
    with st.expander("🔍 Search Filters", expanded=False):
        result_limit = st.slider("Number of results", min_value=1, max_value=10, value=5)
        selected_resource_id = st.number_input("Resource ID", min_value=0, step=1)
        selected_permission_filter = st.selectbox("Permissions Filter", ["Any"] + permissions)
        selected_category_filter = st.selectbox("Category Filter", ["Any"] + list(categories.keys()))
        selected_subsection_filter = st.selectbox("Subsection Filter", ["Any"] + list(subsections.keys()))
        selected_learning_type_filter = st.selectbox("Learning Type Filter", ["Any"] + list(learning_types.keys()))

    # Main search area
    st.subheader("🔎 Search Documents")
    search_query = st.text_input("Enter your search query", placeholder="Type your search terms here...")

    

    # Prepare filters
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

    # Search button
    if st.button("🔍 Search", use_container_width=True):
        if search_query:
            with st.spinner('🔄 Searching... Please wait.'):
                import time

                # Perform searches and measure time for DocumentRetriever
                doc_retriever_start = time.time()
                search_results = search_documents(
                    search_query,
                    limit=result_limit,
                    resource_id=selected_resource_id if selected_resource_id != 0 else None,
                    permissions_allowed=selected_permission_filter if selected_permission_filter != "Any" else None,
                    category_id=categories[selected_category_filter] if selected_category_filter != "Any" else None,
                    sub_section_id=subsections[selected_subsection_filter] if selected_subsection_filter != "Any" else None,
                    learning_type_id=learning_types[selected_learning_type_filter] if selected_learning_type_filter != "Any" else None,
                )
                doc_retriever_time = time.time() - doc_retriever_start

                # Measure time for LangChain search
                langchain_start = time.time()
                search_langchain_results = langchain_processor.similarity_search_with_scores(
                    search_query,
                    k=result_limit,
                    filter=langchain_filters
                )
                langchain_time = time.time() - langchain_start

                # Display results in tabs
                result_tab1, result_tab2 = st.tabs(["📑 DocumentRetriever", "🔗 LangchainProcessor"])

                with result_tab1:
                    if search_results:
                        st.info(f"⏱️ DocumentRetriever search time: {doc_retriever_time:.2f} seconds")

                        for idx, result in enumerate(search_results, 1):
                            with st.container():
                                st.markdown(f"### Result {idx}")
                                st.markdown(f"**Content:** {result['content']}")
                                st.markdown(f"**Resource:** {result['resource_name']}")
                                st.markdown(f"**Relevance Score:** {result['distance']}")
                                st.divider()
                    else:
                        st.info("No results found in DocumentRetriever.")

                with result_tab2:
                    if search_langchain_results:
                        st.info(f"⏱️ LangChain search time: {langchain_time:.2f} seconds")

                        for idx, (doc, score) in enumerate(search_langchain_results, 1):
                            with st.container():
                                st.markdown(f"### Result {idx}")
                                st.markdown(f"**Content:** {doc.page_content}")
                                st.markdown(f"**Resource:** {doc.metadata.get('resource_name', 'N/A')}")
                                st.markdown(f"**Relevance Score:** {score}")
                                st.divider()
                    else:
                        st.info("No results found in LangchainProcessor.")
        else:
            st.warning("⚠️ Please enter a search query.")