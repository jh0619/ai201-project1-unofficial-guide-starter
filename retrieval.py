"""
retrieval.py — Embed chunks and build a ChromaDB vector store, then query it.

Usage:
    python retrieval.py
        Builds (or rebuilds) the vector store from chunks.json.

    from retrieval import get_collection, get_embedding_model, query
        Use these in other scripts (test_retrieval.py, generation, UI).
"""

import json
import os

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = "chunks.json"
PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "interview_chunks"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# ─────────────────────────────────────────────
# STEP 1: Load chunks produced by ingest.py
# ─────────────────────────────────────────────

def load_chunks(chunks_file: str = CHUNKS_FILE) -> list[dict]:
    """Load the chunks.json produced by ingest.py."""
    if not os.path.exists(chunks_file):
        raise FileNotFoundError(
            f"{chunks_file} not found. Run ingest.py first (Milestone 3)."
        )
    with open(chunks_file, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# STEP 2: Embedding model
# ─────────────────────────────────────────────

def get_embedding_model() -> SentenceTransformer:
    """
    Load the sentence-transformers embedding model.

    all-MiniLM-L6-v2 runs locally, no API key, no rate limits.
    Produces 384-dimensional embeddings.
    """
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


# ─────────────────────────────────────────────
# STEP 3: Build / load the ChromaDB vector store
# ─────────────────────────────────────────────

def get_chroma_client(persist_dir: str = PERSIST_DIR) -> chromadb.PersistentClient:
    """Return a persistent ChromaDB client that saves to disk."""
    return chromadb.PersistentClient(path=persist_dir)


def build_vector_store(
    chunks: list[dict],
    embedding_model: SentenceTransformer,
    persist_dir: str = PERSIST_DIR,
    collection_name: str = COLLECTION_NAME,
):
    """
    Embed all chunks and store them in a ChromaDB collection.

    Each chunk's text is embedded, and its metadata (source, url, company,
    filename, chunk_id) is stored alongside it for later attribution.

    Uses cosine distance so that scores are intuitive: 0 = identical,
    higher = less similar.
    """
    client = get_chroma_client(persist_dir)

    # Drop any existing collection so we don't get duplicate entries
    # if this script is run more than once.
    existing = [c.name for c in client.list_collections()]
    if collection_name in existing:
        client.delete_collection(collection_name)

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # cosine distance for sentence embeddings
    )

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "url": c["url"],
            "company": c["company"],
            "filename": c["filename"],
        }
        for c in chunks
    ]

    print(f"Embedding {len(texts)} chunks with {EMBEDDING_MODEL_NAME}...")
    embeddings = embedding_model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB collection '{collection_name}'")
    return collection


def get_collection(persist_dir: str = PERSIST_DIR, collection_name: str = COLLECTION_NAME):
    """Get an existing ChromaDB collection (assumes build_vector_store already ran)."""
    client = get_chroma_client(persist_dir)
    return client.get_collection(name=collection_name)


# ─────────────────────────────────────────────
# STEP 4: Query function
# ─────────────────────────────────────────────

# Companies present in the corpus. Used to detect when a query is
# explicitly about one company so we can filter retrieval to it.
KNOWN_COMPANIES = ["Bloomberg", "Apple", "Google", "Amazon"]


def detect_company(question: str) -> str | None:
    """
    Return a company name if the question explicitly mentions one of the
    companies in our corpus, otherwise None.
    """
    q_lower = question.lower()
    for company in KNOWN_COMPANIES:
        if company.lower() in q_lower:
            return company
    return None


def query(
    question: str,
    collection,
    embedding_model: SentenceTransformer,
    k: int = 5,
    company_filter: str | None = "auto",
) -> list[dict]:
    """
    Run semantic search for `question` against the vector store.

    company_filter:
        "auto" (default) — detect a company from the question and, if found,
                           restrict retrieval to that company's chunks.
        None             — no filtering, pure semantic search over all chunks.
        "<Company>"      — force filtering to a specific company.
    """
    query_embedding = embedding_model.encode([question]).tolist()

    if company_filter == "auto":
        active_filter = detect_company(question)
    else:
        active_filter = company_filter

    where_clause = {"company": active_filter} if active_filter else None

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        where=where_clause,
    )

    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "chunk_id": results["ids"][0][i],
            "text":     results["documents"][0][i],
            "distance": results["distances"][0][i],
            **results["metadatas"][0][i],
        })

    return output


# ─────────────────────────────────────────────
# MAIN — build the vector store from chunks.json
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("Milestone 4: Building vector store")
    print("=" * 50)

    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    model = get_embedding_model()
    collection = build_vector_store(chunks, model)

    # Quick sanity check query
    print("\n" + "=" * 50)
    print("Sanity check query")
    print("=" * 50)
    sample_results = query("Does Bloomberg new grad interview include system design?", collection, model, k=3)
    for r in sample_results:
        print(f"\n[{r['company']} | {r['source']} | distance={r['distance']:.3f}]")
        print(r["text"][:200] + "...")
