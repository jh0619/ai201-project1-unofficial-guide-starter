"""
ingest.py — Document ingestion and chunking pipeline

Usage:
    python ingest.py

Outputs:
    - Prints total document count and chunk count
    - Saves chunks to chunks.json for use in Milestone 4
"""

import os
import re
import json

# ─────────────────────────────────────────────
# STEP 1: Load raw .txt files from /docs folder
# ─────────────────────────────────────────────


def load_documents(folder_path: str) -> list[dict]:
    """
    Load all .txt files from folder_path.
    Returns a list of dicts: {text, source, url, company}
    """
    documents = []

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Docs folder not found: {folder_path}")

    for filename in sorted(os.listdir(folder_path)):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()

        # Parse header metadata (SOURCE:, URL:, COMPANY:)
        metadata = parse_header(raw)
        body = extract_body(raw)

        documents.append({
            "filename": filename,
            "source":   metadata.get("SOURCE", "unknown"),
            "url":      metadata.get("URL", ""),
            "company":  metadata.get("COMPANY", "unknown"),
            "text":     body,
        })
        print(f"  Loaded: {filename} ({len(body)} chars)")

    return documents


def parse_header(raw: str) -> dict:
    """
    Parse the metadata header lines before the --- separator.
    Handles lines like: SOURCE: Blind
    """
    metadata = {}
    if "---" not in raw:
        return metadata

    header_section = raw.split("---")[0]
    for line in header_section.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip().upper()] = value.strip()
    return metadata


def extract_body(raw: str) -> str:
    """
    Return only the text after the --- separator.
    """
    if "---" in raw:
        return raw.split("---", 1)[1].strip()
    return raw.strip()


# ─────────────────────────────────────────────
# STEP 2: Clean each document
# ─────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Remove noise from forum posts:
    - HTML tags and entities
    - Navigation / UI boilerplate
    - Repeated whitespace
    """

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode common HTML entities
    html_entities = {
        "&amp;": "&", "&nbsp;": " ", "&quot;": '"',
        "&lt;": "<", "&gt;": ">", "&#39;": "'",
        "&apos;": "'",
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Remove leftover URL-only lines
    text = re.sub(r"https?://\S+", "", text)

    # Remove common forum boilerplate phrases
    boilerplate = [
        r"Sign in to see more.*",
        r"Read more.*",
        r"Share\s*$",
        r"Helpful\s*$",
        r"Reply\s*$",
        r"Like\s*$",
        r"\d+ comments?",
        r"Hide company name",
        r"Post\s*$",
        r"Community Guidelines.*",
        r"Copyright ©.*",
        r"Download App.*",
        r"^New$",
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


# ─────────────────────────────────────────────
# STEP 3: Chunk each document
# ─────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    """
    Split text into overlapping character-level chunks.

    chunk_size: target size of each chunk in characters (~2-4 sentences)
    overlap:    number of characters shared between adjacent chunks

    Why character-level: forum posts don't have consistent paragraph
    structure, so sentence/paragraph splitting is fragile. Fixed-size
    with overlap is more predictable for short, uneven review text.
    """
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If we're not at the end, try to break at a sentence boundary
        # Look for ". " or "\n" within the last 60 characters of the window
        if end < len(text):
            # Search backwards for a clean break point
            break_chars = [". ", ".\n", "\n\n", "\n", "! ", "? "]
            best_break = end
            for bc in break_chars:
                idx = text.rfind(bc, start + chunk_size - 60, end)
                if idx != -1:
                    best_break = idx + len(bc)
                    break
            end = best_break

        chunk = text[start:end].strip()

        # Only keep chunks with real content (skip empty / whitespace-only)
        if len(chunk) > 80:
            chunks.append(chunk)

        # Move forward, but back up by overlap characters
        start = end - overlap

        # Safety: if overlap would cause infinite loop, advance
        if start >= end:
            start = end

    return chunks


# ─────────────────────────────────────────────
# STEP 4: Attach metadata and save
# ─────────────────────────────────────────────

def build_chunks(documents: list[dict], chunk_size: int = 400, overlap: int = 80) -> list[dict]:
    """
    Chunk all documents and attach source metadata to each chunk.
    Returns list of dicts: {text, source, url, company, filename, chunk_id}
    """
    all_chunks = []

    for doc in documents:
        cleaned = clean_text(doc["text"])
        chunks = chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)

        for i, chunk_text_val in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{doc['filename']}__chunk_{i}",
                "text":     chunk_text_val,
                "source":   doc["source"],
                "url":      doc["url"],
                "company":  doc["company"],
                "filename": doc["filename"],
            })

    return all_chunks


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    DOCS_FOLDER = "docs"
    CHUNK_SIZE = 400
    OVERLAP = 80
    OUTPUT_FILE = "chunks.json"

    print("=" * 50)
    print("STEP 1: Loading documents")
    print("=" * 50)
    documents = load_documents(DOCS_FOLDER)
    print(f"\nTotal documents loaded: {len(documents)}\n")

    print("=" * 50)
    print("STEP 2: Cleaning + Chunking")
    print("=" * 50)
    chunks = build_chunks(documents, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
    print(f"\nTotal chunks produced: {len(chunks)}")

    # Sanity check
    if len(chunks) < 50:
        print("WARNING: Fewer than 50 chunks — your documents may be too short or chunks too large.")
    elif len(chunks) > 2000:
        print("WARNING: More than 2000 chunks — chunks may be too small.")
    else:
        print("Chunk count looks healthy (50–2000 range).")

    # Save to JSON for Milestone 4
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(chunks)} chunks to {OUTPUT_FILE}")
