import openai
from src.db.db_manager import DatabaseManager
import os
# Function to get embeddings from OpenAI
db_manager = DatabaseManager()
openai.api_key = os.getenv("OPENAI_API_KEY")
def get_embedding(text):
    response = openai.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding


def search_documents(query, limit=5, resource_id=None, permissions_allowed=None, category_id=None, sub_section_id=None, learning_type_id=None):
    query_embedding = get_embedding(query)
    result = db_manager.search_documents(query_embedding, limit,resource_id=resource_id, permissions_allowed=permissions_allowed, category_id=category_id, sub_section_id=sub_section_id, learning_type_id=learning_type_id)
    print("Search results:", result)
    return result

if __name__ == "__main__":
    search_documents("diabetes in the world ")
    
    