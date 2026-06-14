"""
generate.py — Grounded answer generation using retrieved chunks + Groq LLM.

The core engineering goal here is GROUNDING: the LLM must answer ONLY from
the retrieved chunks, never from its training knowledge. If the chunks don't
contain the answer, it must say so.

Usage:
    from generate import ask
    result = ask("Does Bloomberg new grad include system design?")
    print(result["answer"])
    print(result["sources"])
"""

import os

from dotenv import load_dotenv
from groq import Groq

from retrieval import get_collection, get_embedding_model, query


# ─────────────────────────────────────────────
# Setup: load API key and shared resources once
# ─────────────────────────────────────────────

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

# Load these once at import time so the UI doesn't reload them per query.
_client = None
_collection = None
_embedding_model = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not found. Add it to your .env file "
                "(get a free key at console.groq.com)."
            )
        _client = Groq(api_key=api_key)
    return _client


def _get_resources():
    global _collection, _embedding_model
    if _collection is None:
        _collection = get_collection()
    if _embedding_model is None:
        _embedding_model = get_embedding_model()
    return _collection, _embedding_model


# ─────────────────────────────────────────────
# Prompt construction
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an assistant that answers questions about software \
engineering interview experiences using ONLY the provided context documents.

STRICT RULES:
1. Answer using ONLY information found in the CONTEXT below. Do not use any \
outside or general knowledge about these companies or their interviews.
2. If the context does not contain enough information to answer the question, \
respond with exactly: "I don't have enough information on that."
3. Do not invent details, numbers, round counts, or company specifics that are \
not explicitly stated in the context.
4. When you state a fact, it must be traceable to the context. Be concise."""


def build_user_prompt(question: str, chunks: list[dict]) -> str:
    """
    Assemble the context block from retrieved chunks + the user question.
    Each chunk is labeled with its source filename so the model can ground
    its answer in specific documents.
    """
    context_blocks = []
    for i, c in enumerate(chunks, 1):
        context_blocks.append(
            f"[Document {i} — source: {c['filename']} | {c['company']} / {c['source']}]\n"
            f"{c['text']}"
        )
    context = "\n\n".join(context_blocks)

    return (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        f"Answer using only the context above. "
        f"If the context is insufficient, say you don't have enough information."
    )


# ─────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────

def ask(question: str, k: int = 5) -> dict:
    """
    End-to-end: retrieve relevant chunks, generate a grounded answer,
    and return the answer plus the list of source documents it drew from.

    Returns:
        {
            "answer":  str,
            "sources": list[str],   # unique source filenames + URLs
            "chunks":  list[dict],  # the retrieved chunks (for inspection)
        }
    """
    collection, embedding_model = _get_resources()

    # 1. Retrieve
    chunks = query(question, collection, embedding_model, k=k)

    # Guard: if retrieval returns nothing, don't even call the LLM
    if not chunks:
        return {
            "answer": "I don't have enough information on that.",
            "sources": [],
            "chunks": [],
        }

    # 2. Generate (grounded)
    client = _get_client()
    user_prompt = build_user_prompt(question, chunks)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,  # low temp = stick close to the context, less invention
    )
    answer = response.choices[0].message.content.strip()

    # 3. Attribution — built programmatically from retrieved chunks,
    #    NOT left to the LLM. Dedupe by filename, keep the URL.
    seen = set()
    sources = []
    for c in chunks:
        if c["filename"] not in seen:
            seen.add(c["filename"])
            sources.append(f"{c['filename']} ({c['url']})")

    # If the model declined to answer, suppress sources to avoid implying
    # the answer came from these docs.
    if answer.strip().lower().startswith("i don't have enough information"):
        sources = []

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }


# ─────────────────────────────────────────────
# Quick CLI test
# ─────────────────────────────────────────────

if __name__ == "__main__":
    test_questions = [
        "What is the interview format for Bloomberg new grad SWE?",
        "What types of coding questions appear in Google L3 new grad interviews?",
        "What is the meal plan price at Northeastern University?",  # not in corpus
    ]

    for q in test_questions:
        print("=" * 70)
        print(f"Q: {q}")
        print("=" * 70)
        result = ask(q)
        print(f"\nANSWER:\n{result['answer']}\n")
        print("SOURCES:")
        if result["sources"]:
            for s in result["sources"]:
                print(f"  • {s}")
        else:
            print("  (none — system declined to answer)")
        print()
