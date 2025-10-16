import pymongo
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.embeddings import HuggingFaceEmbeddings
import json
from typing import List, Dict, Any

load_dotenv()

# mongodb connection
mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
mongo_db_name = os.getenv('MONGO_DB_NAME', 'eotdl')
print(f"Connecting to MongoDB...")
mongo_client = pymongo.MongoClient(mongo_url)
db = mongo_client[mongo_db_name]
try:
    # Test the connection
    print("✅ Successfully connected to MongoDB!")
    print(f"Database: {mongo_db_name}")
    print(f"Collections: {db.list_collection_names()}")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    print("Make sure MongoDB is running: docker-compose up -d eotdl-mongo")

# Setup Qdrant client
qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
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
except Exception as e:
    print(f"❌ Failed to connect to Qdrant: {e}")
    print("Make sure Qdrant is running: docker-compose up -d eotdl-qdrant")

# Setup embeddings model (same as in your MCP server)
model_name = "nasa-impact/nasa-smd-ibm-st-v2"
encode_kwargs = {"normalize_embeddings": True}
print(f"Loading embedding model: {model_name}")
try:
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs=encode_kwargs
    )
    print("✅ Embedding model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load embedding model: {e}")
    print("Make sure you have the required dependencies installed")

# Create or get the EOTDL collection in Qdrant
collection_name = "EOTDL"
vector_size = 768  # This should match your embedding model's output size
try:
    # Check if collection exists
    collections = qdrant_client.get_collections()
    collection_exists = any(c.name == collection_name for c in collections.collections)
    if not collection_exists:
        print(f"Creating collection: {collection_name}")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"✅ Collection '{collection_name}' created successfully!")
    else:
        print(f"✅ Collection '{collection_name}' already exists!")
        
except Exception as e:
    print(f"❌ Failed to create/get collection: {e}")

def should_update_item(item: Dict[str, Any], existing_point: Dict[str, Any] = None) -> bool:
    """Check if an item should be updated based on modification time."""
    if not existing_point:
        return True  # New item, should be added
    
    item_updated = item.get('updatedAt', '')
    existing_updated = existing_point.get('payload', {}).get('updated_at', '')
    
    # If no update time info, always update to be safe
    if not item_updated or not existing_updated:
        return True
    
    return str(item_updated) != str(existing_updated)

def extract_text_content(item: Dict[str, Any], item_type: str) -> str:
    """Extract and format text content from datasets, models, or pipelines for vectorization."""
    content_parts = []
    content_parts.append(f"Type: {item_type}")
    content_parts.append(f"Name: {item.get('name', '')}")
    content_parts.append(f"Description: {item.get('metadata', {}).get('description', '')}")
    if item.get('tags'):
        content_parts.append(f"Tags: {', '.join(item['tags'])}")
    return " | ".join(content_parts)

def populate_vector_database(items: List[Dict[str, Any]], item_type: str, start_id: int = 0):
    """Populate the vector database with datasets, models, and pipelines."""
    print(f"\n📊 Processing {len(items)} {item_type}s...")
    try:
        print(f"Found {len(items)} active {item_type}s")
        dataset_points = []
        for i, item in enumerate(items):
            try:
                # Extract text content
                text_content = extract_text_content(item, item_type)
                # Generate embedding
                embedding = embeddings.embed_query(text_content)
                # Create point for Qdrant
                # Use MongoDB ObjectId hash as integer ID for consistent updates
                mongo_id_str = str(item['_id'])
                # Create a consistent integer ID from MongoDB ObjectId
                point_id = hash(mongo_id_str) % (2**63 - 1)  # Ensure positive integer
                if point_id < 0:
                    point_id = -point_id
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "type": item_type,
                        "name": item['name'],
                        "id": item['id'],
                        "description": item['metadata'].get('description', ''),
                        "tags": item['tags'] if item['tags'] else [],
                        "content": text_content,
                    }
                )
                dataset_points.append(point)
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(items)} {item_type}s")
            except Exception as e:
                print(f"❌ Error processing {item_type} {item['name']}: {e}")
                continue
        # Upload dataset points to Qdrant
        if dataset_points:
            qdrant_client.upsert(
                collection_name=collection_name,
                points=dataset_points
            )
            print(f"✅ Uploaded {len(dataset_points)} {item_type} points to Qdrant")
            return len(dataset_points)
        return 0
    except Exception as e:
        print(f"❌ Error processing {item_type}s: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 Starting vector database population...")
    
    datasets = list(db.datasets.find({"active": True}))
    models = list(db.models.find({"active": True}))
    pipelines = list(db.pipelines.find({"active": True}))
    
    total_points = 0
    current_id = 0
    
    # Process datasets first
    if datasets:
        points_added = populate_vector_database(datasets, "dataset", start_id=current_id)
        total_points += points_added
        current_id += len(datasets)
    
    # Process models next
    if models:
        points_added = populate_vector_database(models, "model", start_id=current_id)
        total_points += points_added
        current_id += len(models)
    
    # Process pipelines last
    if pipelines:
        points_added = populate_vector_database(pipelines, "pipeline", start_id=current_id)
        total_points += points_added
    
    print(f"\n🎉 Vector database population completed!")
    print(f"Total points uploaded: {total_points}")
    
    # Get collection info
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        print(f"Collection '{collection_name}' now contains {collection_info.points_count} points")
    except Exception as e:
        print(f"Could not retrieve collection info: {e}")
