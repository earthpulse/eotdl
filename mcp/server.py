from mcp.server.fastmcp import FastMCP
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from typing import List
import json
import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings

mcp = FastMCP("EOTDL_RETRIEVER")

load_dotenv()

qdrant_url = os.environ["QDRANT_URL"]
qdrant_api_key = os.environ["QDRANT_API_KEY"]

# Load the embeddings model
model_name = "nasa-impact/nasa-smd-ibm-st-v2" # Use the embedding model you prefer
encode_kwargs = {"normalize_embeddings": True}
indus_embd = HuggingFaceEmbeddings(
    model_name=model_name,  encode_kwargs=encode_kwargs
)

# Format retrieved documents:
def format_docs(docs):
  doc_str = ''
  for i, doc in enumerate(docs):
    doc_str += f'Resource: {i+1}\n'
    doc_str += f'NAME: {doc.metadata.get("name", "No name")}\n' 
    doc_str += f'URL: {doc.metadata.get("url", "No url")}\n\n' 
    # Add here all the other metadata you want to show to the user
    doc_str += f'{doc.page_content}\n\n'
  return doc_str

# Let's define our retriever class to have a nice interface
class QdrantRetriever():
    def __init__(self, collection_name='EOTDL', k: int = 3):
        self._client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.embedding = indus_embd
        self.collection_name = collection_name
        self.k = k


    def get_relevant_documents(self, query: str) -> List[Document]:
        query_emb = self.embedding.embed_query(query)

        search_result = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_emb,
            limit=self.k,
        )

        docs = []
        for hit in search_result:
            # Adjust based on your actual data structure
            data = hit.payload
            content = data.get("content", "")
            metadata = {}
            for key, value in data.items():
                if key != "content":
                    metadata[key] = value
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
    # Get kwargs
    # 1. Init Retriever
    qdrant_retriever = QdrantRetriever()
    # 2. Get docs
    docs = qdrant_retriever.get_relevant_documents(query)
    # 3. Format and return
    return format_docs(docs)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()