from fastmcp import FastMCP
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from typing import List
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("EOTDL_RETRIEVER")

qdrant_url = os.environ["QDRANT_URL"]
qdrant_api_key = os.environ["QDRANT_API_KEY"]

# Load the embeddings model
model_name = "nasa-impact/nasa-smd-ibm-st-v2" # Use the embedding model you prefer
encode_kwargs = {"normalize_embeddings": True}
indus_embd = HuggingFaceEmbeddings(
    model_name=model_name,  encode_kwargs=encode_kwargs
)

# Format retrieved documents for display
def format_docs(docs):
    doc_str = ''
    for i, doc in enumerate(docs, 1):
        doc_str += f"Type: {doc.metadata.get('type', 'Unknown')}\n"
        doc_str += f"Name: {doc.metadata.get('name', 'No Name')}\n"
        # Truncate description to 200 characters, like test_vector_db.ipynb
        description = doc.metadata.get('description', 'No description')
        doc_str += f"Description: {description}...\n"
        doc_str += f"Tags: {doc.metadata.get('tags', 'No tags')}\n"
        doc_str += "\n"
    return doc_str

# Let's define our retriever class to have a nice interface
class QdrantRetriever():
    def __init__(self, collection_name='EOTDL', k: int = 3):
        if qdrant_api_key:
            qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            qdrant_client = QdrantClient(url=qdrant_url)
        self._client = qdrant_client
        # Test connection
        collections = self._client.get_collections()
        logging.info("✅ Successfully connected to Qdrant!")
        logging.info(f"Existing collections: {[c.name for c in collections.collections]}")
        self.embedding = indus_embd
        self.collection_name = collection_name
        self.k = k

    def get_relevant_documents(self, query: str) -> List[Document]:
        query_emb = self.embedding.embed_query(query)
        search_result = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_emb,
            limit=self.k
        )
        docs = []
        for hit in search_result:
            data = hit.payload
            # try to find the content (document body) in different possible keys
            content = data.get("content") or data.get("description", "")
            metadata = {}
            for key, value in data.items():
                if key != "content" and key != "description":
                    metadata[key] = value
            # Optionally add description into metadata if content comes from "content"
            if "description" in data:
                metadata["description"] = data["description"]
            docs.append(Document(page_content=content, metadata=metadata))
        return docs

@mcp.tool()
def rag_search(query: str) -> str:
    """
    Get relevant documents for answering Earth Observation queries.
    Args:
        query: Query string for the retrieval
    :return:
    """
    qdrant_retriever = QdrantRetriever()
    docs = qdrant_retriever.get_relevant_documents(query)
    return format_docs(docs)

if __name__ == "__main__":
    # Initialize and run the server
    # mcp.run()
    mcp.run(transport="http", host="0.0.0.0", port=8000)