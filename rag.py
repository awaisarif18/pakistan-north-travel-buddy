"""Persistent Gemini embeddings and basic semantic retrieval. No chat generation."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "chroma"
COLLECTION_NAME = "north_tours"
DIMENSIONS = 3072
load_dotenv(ROOT / ".env")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2").strip()
INDEX_CONFIG = {
    "embedding_model": EMBEDDING_MODEL,
    "dimensions": DIMENSIONS,
    "retrieval_format": "search-result-v1",
}
QUESTIONS = [
    "Where should I refuel before traveling to Khunjerab Pass?",
    "What is the best season for Rakaposhi Base Camp?",
    "What transport options are available from Islamabad to Skardu?",
    "What are the trekking options near Hunza?",
    "What fuel precautions are necessary when crossing Babusar Pass?",
]


def gemini_client():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "your-gemini-api-key":
        raise ValueError("Set GEMINI_API_KEY in .env before embedding.")
    return genai.Client(api_key=key, http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(
            attempts=4, initial_delay=2, max_delay=20,
            http_status_codes=[429, 500, 502, 503, 504],
        ),
    ))


def embed(client, text, *, document=False):
    # Embedding 2 uses prompt prefixes instead of the task_type API parameter.
    if EMBEDDING_MODEL.startswith("gemini-embedding-2"):
        content = (f"title: Pakistan North Tours | text: {text}" if document
                   else f"task: search result | query: {text}")
        config = types.EmbedContentConfig(output_dimensionality=DIMENSIONS)
    else:
        content = text
        config = types.EmbedContentConfig(
            output_dimensionality=DIMENSIONS,
            task_type="RETRIEVAL_DOCUMENT" if document else "RETRIEVAL_QUERY",
        )
    response = client.models.embed_content(model=EMBEDDING_MODEL, contents=content, config=config)
    if not response.embeddings or len(response.embeddings) != 1:
        raise ValueError("Expected one embedding for one input; no vector was saved.")
    vector = response.embeddings[0].values
    if vector is None or len(vector) != DIMENSIONS:
        raise ValueError(f"Expected {DIMENSIONS} vector dimensions; no vector was saved.")
    return vector


def open_collection(*, create=False):
    if not create and not (DB_PATH / "chroma.sqlite3").exists():
        raise ValueError("Index missing. Run python ingest.py --embed first.")
    db = chromadb.PersistentClient(path=str(DB_PATH))
    if create:
        collection = db.get_or_create_collection(
            COLLECTION_NAME, embedding_function=None, metadata=INDEX_CONFIG,
            configuration={"hnsw": {"space": "cosine"}},
        )
    else:
        collection = db.get_collection(COLLECTION_NAME, embedding_function=None)
    if any(collection.metadata.get(key) != value for key, value in INDEX_CONFIG.items()):
        raise ValueError("Index embedding settings differ from .env. Restore the indexed model settings.")
    return collection


def build_index():
    path = DATA_DIR / "chunks.json"
    if not path.is_file():
        raise ValueError("Chunks missing. Run python ingest.py first.")
    chunks = json.loads(path.read_text(encoding="utf-8"))
    ids = [chunk["id"] for chunk in chunks]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Chunks must have nonempty, unique IDs.")
    collection = open_collection(create=True)
    stored = collection.get(include=["documents", "metadatas"])
    existing = dict(zip(stored["ids"], zip(stored["documents"], stored["metadatas"])))
    if set(existing) - set(ids):
        raise ValueError("Index contains different chunks. Review the changed PDF before rebuilding.")
    for chunk in chunks:
        if chunk["id"] in existing and existing[chunk["id"]] != (chunk["text"], chunk["metadata"]):
            raise ValueError(f"Indexed text or pages changed for {chunk['id']}. Review before rebuilding.")
    pending = [chunk for chunk in chunks if chunk["id"] not in existing]
    print(f"Existing vectors reused: {len(existing)}; embeddings needed: {len(pending)}", flush=True)
    if pending:
        with gemini_client() as client:
            for number, chunk in enumerate(pending, 1):
                vector = embed(client, chunk["text"], document=True)
                collection.add(ids=[chunk["id"]], embeddings=[vector],
                               documents=[chunk["text"]], metadatas=[chunk["metadata"]])
                print(f"Saved {number}/{len(pending)}: {chunk['id']}", flush=True)
                if number < len(pending):
                    time.sleep(1)
    print(f"Indexed chunks: {collection.count()}; model: {EMBEDDING_MODEL}; dimensions: {DIMENSIONS}")
    print(f"Chroma location: {DB_PATH}")
    return collection


def query_embedding(client, question):
    path = DATA_DIR / "query_embeddings.json"
    cache = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    key = hashlib.sha256(json.dumps([INDEX_CONFIG, question], sort_keys=True).encode()).hexdigest()
    if key not in cache:
        cache[key] = embed(client, question)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(cache) + "\n", encoding="utf-8")
        temporary.replace(path)
    return cache[key]


def retrieve(collection, client, question, top_k=5):
    if not question.strip():
        raise ValueError("Enter a nonempty question.")
    count = collection.count()
    if not count:
        raise ValueError("Index is empty. Run python ingest.py --embed first.")
    result = collection.query(query_embeddings=[query_embedding(client, question)],
                              n_results=min(top_k, count),
                              include=["documents", "metadatas", "distances"])
    return [
        {"id": chunk_id, "text": text, "metadata": metadata, "distance": distance}
        for chunk_id, text, metadata, distance in zip(
            result["ids"][0], result["documents"][0],
            result["metadatas"][0], result["distances"][0],
        )
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", help="Omit to run the five baseline questions.")
    args = parser.parse_args()
    collection = open_collection()
    results = []
    output = DATA_DIR / "retrieval_results.json"
    with gemini_client() as client:
        for question in [args.question] if args.question else QUESTIONS:
            matches = retrieve(collection, client, question)
            results.append({"question": question, "matches": matches})
            output.write_text(json.dumps({"config": INDEX_CONFIG, "results": results},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"\n{question}", flush=True)
            for rank, match in enumerate(matches[:3], 1):
                metadata = match["metadata"]
                print(f"{rank}. {match['id']} | PDF pages {metadata['page_start']}-{metadata['page_end']}"
                      f" | cosine distance {match['distance']:.4f}", flush=True)
            time.sleep(1)
    print(f"\nFull passages and top-five results: {output}")


if __name__ == "__main__":
    try:
        main()
    except errors.APIError as error:
        raise SystemExit(f"Gemini API error {error.code}. Check model access, API key, or quota. "
                         "Completed embeddings are saved; rerun to resume.") from None
    except ValueError as error:
        raise SystemExit(str(error)) from None
