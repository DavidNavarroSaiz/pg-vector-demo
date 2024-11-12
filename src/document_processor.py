# main.py
from src.db.db_manager import DatabaseManager
from src.document_loader import UniversalDocumentProcessor
from src.langchain_processor import LangchainProcessor
from langchain.docstore.document import Document
from pathlib import Path
import re
import uuid


def is_url(path):
    # Check if path is a URL
    url_regex = re.compile(r'^(https?://)?(www\.)?([a-zA-Z0-9_-]+)+(\.[a-zA-Z]+)+(/[\w#!:.?+=&%@!\-]*)?$')
    return re.match(url_regex, path) is not None

def process_and_store_document(doc_path, section_id, sub_section_id, learning_type_id, category_id, permissions_allowed="paid", langchain_db=False):

    db_manager = DatabaseManager()
    doc_processor = UniversalDocumentProcessor()
    langchain_processor = LangchainProcessor()


    if is_url(doc_path):
        resource_name = doc_path
    else:
        # Extract the filename from the doc_path
        resource_name = Path(doc_path).name

    # Check existing resource names in the database
    db_sources = db_manager.get_all_resource_paths()
    print(f"Existing document paths: {db_sources}")

    # Check if the document is already in the database based on the filename
    if resource_name not in db_sources:
        # Step 1: Process the document and generate a summary
        result = doc_processor.process(doc_path)
        summary = result.get("summary", "")

        if summary:
            # Step 2: Create a Document object with metadata
            doc = Document(
                page_content=summary,
                metadata={
                    'path': resource_name,  # Use only the filename here
                    'resource_name': resource_name,  # Store only the filename
                    'summary': True,
                    'category_id': category_id,
                    'sub_section_id': sub_section_id,
                    'section_id': section_id,
                    'learning_type_id': learning_type_id,
                    'permissions_allowed': permissions_allowed
                }
            )

            # Step 3: Add the resource to the database and get the resource ID
            resource_id = db_manager.add_resource(
                sub_section_id=sub_section_id,
                learning_type_id=learning_type_id,
                category_id=category_id,
                resource_name=resource_name,  # Store only the filename
                path=resource_name,  # Store only the filename
                permissions_allowed=permissions_allowed
            )

            # Step 4: Split the document into chunks
            chunks_docs = doc_processor.split_docs([doc])

            # Prepare each chunk for LangchainProcessor with additional metadata
            for order, chunk in enumerate(chunks_docs):

                # Add the `order` and `unique_id` to chunk metadata
                chunk.metadata['vector_order'] = order

            # Initialize LangchainProcessor and add documents with metadata
            langchain_processor.add_documents([chunk for chunk in chunks_docs])

            # Step 5: Add each chunk as an embedding to the database
            for order, chunk in enumerate(chunks_docs):
                embedding = doc_processor.get_embedding(chunk.page_content)

                # Add chunk to the database with its metadata and embedding
                db_manager.add_chunk(
                    resource_id=resource_id,
                    chunk_order=order,
                    embedding=embedding,
                    content=chunk.page_content,
                    summary=True,
                    cmetadata=chunk.metadata
                )


            print("Document and chunks processed and stored successfully.")
            return f"Document '{resource_name}' uploaded and processed successfully!", result
        else:
            print("No summary generated for the document.")
            return "No summary generated for the document.", None
    else:
        print(f"Document '{resource_name}' already exists in the database.")
        return f"Document '{resource_name}' already exists in the database.", None
        
if __name__=='__main__':
    message, summary = process_and_store_document(
    doc_path="./src/docs/CHWsUniversalTitles.pdf",
    section_id=1,
    sub_section_id=4,
    learning_type_id=5,
    category_id=1,
    permissions_allowed="paid"
)