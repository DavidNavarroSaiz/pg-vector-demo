from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import src.pg_vector_test.langchain as langchain
import openai
import os
langchain.debug = False

load_dotenv()

class PGVectorManager:
    def __init__(self, collection_name="my_docs_test"):
        self.connection = (
            f"postgresql+psycopg://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        self.collection_name = collection_name
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection,
            use_jsonb=True,
        )

    def add_documents(self, docs):
        """Add documents to the vector store."""
        ids = [doc.metadata["id"] for doc in docs]
        self.vector_store.add_documents(docs, ids=ids)
    
    def delete_document(self, doc_id):
        """Delete a document by ID."""
        self.vector_store.delete(ids=[str(doc_id)])
    
    def similarity_search(self, query, k=10, filter=None):
        """Perform a similarity search."""
        return self.vector_store.similarity_search(query, k=k, filter=filter)

    def similarity_search_with_scores(self, query, k=10,filter=None):
        """Perform a similarity search and return results with scores."""
        results = self.vector_store.similarity_search_with_score(query=query, k=k,filter=filter)
        return [(doc, score) for doc, score in results]

    def get_retriever(self, search_type="mmr", k=1):
        """Transform the vector store into a retriever for RAG."""
        return self.vector_store.as_retriever(search_type=search_type, search_kwargs={"k": k})

    def display_results(self, results):
        """Display the search results."""
        for doc in results:
            print(f"* {doc.page_content} [{doc.metadata}]")

# Example usage:
if __name__ == "__main__":
    pg_manager = PGVectorManager()
    
    # docs = [
    #     Document(page_content="there are cats in the pond", metadata={"id": 1, "location": "pond", "topic": "animals"}),
    #     Document(page_content="ducks are also found in the pond", metadata={"id": 2, "location": "pond", "topic": "animals"}),
    #     Document(page_content="fresh apples are available at the market", metadata={"id": 3, "location": "market", "topic": "food"}),
    # ]
    
    # # Add documents
    # pg_manager.add_documents(docs)

    # Perform a similarity search
    
    # query = "kitty"
    # results = pg_manager.similarity_search(query, k=3)
    # pg_manager.display_results(results)

    # # Perform a similarity search with scores
    # results_with_scores = pg_manager.similarity_search_with_scores("cats", k=3,filter={"id": {"$in": [1, 5, 2, 9]}})
    # for doc, score in results_with_scores:
    #     print(f"* [SIM={score:.3f}] {doc.page_content} [{doc.metadata}]")

    # # Delete a document by ID
    # pg_manager.delete_document(3)

    # Retrieve as RAG retriever
    retriever = pg_manager.get_retriever(k=1)
    print(retriever.invoke("cat"))
