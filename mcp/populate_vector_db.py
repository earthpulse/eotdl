import os
import sys
import json
from urllib.request import urlopen
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

api_url = os.getenv("EOTDL_API_URL") or "https://api.eotdl.com"
qdrant_url = os.getenv("QDRANT_URL")
if not qdrant_url:
    raise SystemExit("QDRANT_URL is not set")
qdrant_api_key = os.getenv("QDRANT_API_KEY") or ""
collection_name = "EOTDL"
vector_size = 768
qdrant_client = None
embeddings = None


def fetch_catalog(resource: str) -> List[Dict[str, Any]]:
    print(f"Fetching {resource} from {api_url}...")
    with urlopen(f"{api_url}/{resource}") as response:
        items = json.load(response)
    print(f"Fetched {len(items)} {resource}")
    return items


def extract_text_content(item: Dict[str, Any], item_type: str) -> str:
    metadata = item.get("metadata") or {}
    parts = [
        f"Type: {item_type}",
        f"Name: {item.get('name', '')}",
        f"Description: {metadata.get('description', '')}",
    ]
    if item.get("tags"):
        parts.append(f"Tags: {', '.join(item['tags'])}")
    return " | ".join(parts)


def build_payload(item: Dict[str, Any], item_type: str, text_content: str) -> Dict[str, Any]:
    metadata = item.get("metadata") or {}
    payload = dict(item)
    payload.update({
        "type": item_type,
        "name": item.get("name", ""),
        "id": item.get("id"),
        "description": metadata.get("description", ""),
        "tags": item.get("tags") or [],
        "content": text_content,
        "url": f"https://www.eotdl.com/{item_type}s/{item.get('name', '')}",
        "authors": metadata.get("authors", []),
        "license": metadata.get("license", ""),
        "source": metadata.get("source", ""),
        "thumbnail": metadata.get("thumbnail", ""),
    })
    return payload


def populate_vector_database(items: List[Dict[str, Any]], item_type: str, start_id: int = 0):
    print(f"\n📊 Processing {len(items)} {item_type}s...")
    points = []
    for i, item in enumerate(items):
        try:
            text_content = extract_text_content(item, item_type)
            points.append(PointStruct(
                id=start_id + i,
                vector=embeddings.embed_query(text_content),
                payload=build_payload(item, item_type, text_content),
            ))
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(items)} {item_type}s")
        except Exception as e:
            print(f"❌ Error processing {item_type} {item.get('name')}: {e}")
    if points:
        qdrant_client.upsert(collection_name=collection_name, points=points)
        print(f"✅ Uploaded {len(points)} {item_type} points to Qdrant")
    return len(points)


def recreate_collection():
    names = [c.name for c in qdrant_client.get_collections().collections]
    if collection_name in names:
        print(f"Deleting collection: {collection_name}")
        qdrant_client.delete_collection(collection_name)
    print(f"Creating collection: {collection_name}")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def main():
    global qdrant_client, embeddings

    print(f"Connecting to Qdrant at: {qdrant_url}")
    try:
        qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, check_compatibility=False)
        collections = qdrant_client.get_collections()
        print("✅ Successfully connected to Qdrant!")
        print(f"Existing collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
        sys.exit(1)

    model_name = "nasa-impact/nasa-smd-ibm-st-v2"
    print(f"Loading embedding model: {model_name}")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={"normalize_embeddings": True},
        )
        print("✅ Embedding model loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        sys.exit(1)

    print("🚀 Starting vector database population...")
    datasets = fetch_catalog("datasets")
    models = fetch_catalog("models")
    pipelines = fetch_catalog("pipelines")

    recreate_collection()

    total_points = 0
    current_id = 0
    for items, item_type in ((datasets, "dataset"), (models, "model"), (pipelines, "pipeline")):
        if not items:
            continue
        added = populate_vector_database(items, item_type, start_id=current_id)
        total_points += added
        current_id += len(items)

    print(f"\n🎉 Vector database population completed!")
    print(f"Total points uploaded: {total_points}")
    collection_info = qdrant_client.get_collection(collection_name)
    print(f"Collection '{collection_name}' now contains {collection_info.points_count} points")


if __name__ == "__main__":
    main()
