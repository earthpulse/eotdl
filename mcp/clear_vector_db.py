#!/usr/bin/env python3
"""
Script to clear the vector database before repopulating
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

# Setup Qdrant client
qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
collection_name = "EOTDL"

print(f"Connecting to Qdrant at: {qdrant_url}")
try:
    if qdrant_api_key:
        qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    else:
        qdrant_client = QdrantClient(url=qdrant_url)
    
    # Test connection
    collections = qdrant_client.get_collections()
    print("✅ Successfully connected to Qdrant!")
    print(f"Existing collections: {[c.name for c in collections.collections]}")
    
    # Clear the collection if it exists
    if any(c.name == collection_name for c in collections.collections):
        print(f"🗑️  Clearing collection '{collection_name}'...")
        qdrant_client.delete_collection(collection_name)
        print(f"✅ Collection '{collection_name}' cleared!")
    else:
        print(f"ℹ️  Collection '{collection_name}' does not exist, nothing to clear.")
        
except Exception as e:
    print(f"❌ Failed to connect to Qdrant: {e}")
    print("Make sure Qdrant is running: docker-compose up -d eotdl-qdrant")
