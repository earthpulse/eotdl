from fastmcp import FastMCP
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from typing import List
import os
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logging.basicConfig(level=logging.INFO)

# Load the embeddings model

logging.info(f"Loading embedding model")
indus_embd = HuggingFaceEmbeddings(
    model_name=os.getenv("EMBEDDING_MODEL", "nasa-impact/nasa-smd-ibm-st-v2"), # Use the embedding model you prefe
    encode_kwargs={"normalize_embeddings": True}
)
logging.info(f"Embedding model loaded")

# rag retriever

qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

class QdrantRetriever():
    def __init__(self, collection_name='EOTDL', k: int = 3):
        if qdrant_api_key:
            qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            qdrant_client = QdrantClient(url=qdrant_url)
        self._client = qdrant_client
        collections = self._client.get_collections()
        logging.info("✅ Successfully connected to Qdrant!")
        logging.info(f"Existing collections: {[c.name for c in collections.collections]}")
        self.embedding = indus_embd
        self.collection_name = collection_name
        self.k = k

    def get_relevant_documents(self, query: str) -> List[Document]:
        logging.info(f"Querying Qdrant with query: {query}")
        query_emb = self.embedding.embed_query(query)
        search_result = self._client.query_points(
            collection_name=self.collection_name,
            query=query_emb,
            limit=self.k
        ).points
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
        logging.info(f"Found {len(docs)} documents")
        return docs

qdrant_retriever = QdrantRetriever()

# mcp 

mcp = FastMCP("EOTDL_RETRIEVER")

def format_docs(docs):
    doc_str = ''
    for i, doc in enumerate(docs, 1):
        doc_str += f"Type: {doc.metadata.get('type', 'Unknown')}\n"
        doc_str += f"Name: {doc.metadata.get('name', 'No Name')}\n"
        description = doc.metadata.get('description', 'No description')
        doc_str += f"Description: {description}...\n"
        doc_str += f"Tags: {doc.metadata.get('tags', 'No tags')}\n"
        doc_str += "\n"
    return doc_str

@mcp.tool()
def eotdl_search(query: str) -> str:
    """
    Search for datasets, models, and pipelines in the EOTDL (https://www.eotdl.com/).
    Args:
        query: Query string for the retrieval
    :return: Formatted string of relevant documents
    """
    try:
        docs = qdrant_retriever.search(query)
    except Exception as e:
        logging.error(f"Error searching Qdrant: {e}")
        return "Error searching Qdrant"
    return format_docs(docs)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/")