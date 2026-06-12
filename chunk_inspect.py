"""
chunk_inspect.py — Inspect chunks produced by ingest.py

Usage:
    python chunk_inspect.py

Run this AFTER ingest.py has produced chunks.json.
Prints 5 random chunks so you can verify they are:
  - Readable and self-contained
  - Free of HTML artifacts
  - Correctly attributed to source documents
"""

import json
import random


def inspect_chunks(chunks_file: str = "chunks.json", n: int = 5):
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Total chunks: {len(chunks)}\n")

    # Show distribution by company
    from collections import Counter
    company_counts = Counter(c["company"] for c in chunks)
    print("Chunks by company:")
    for company, count in sorted(company_counts.items()):
        print(f"  {company}: {count} chunks")
    print()

    # Show 5 random chunks
    sample = random.sample(chunks, min(n, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print("=" * 60)
        print(f"CHUNK {i} of {n}")
        print(f"  chunk_id : {chunk['chunk_id']}")
        print(f"  company  : {chunk['company']}")
        print(f"  source   : {chunk['source']}")
        print(f"  length   : {len(chunk['text'])} chars")
        print(f"  url      : {chunk['url']}")
        print("-" * 60)
        print(chunk["text"])
        print()

    # Flag potential problems
    print("=" * 60)
    print("QUALITY CHECKS")
    print("=" * 60)

    empty = [c for c in chunks if len(c["text"].strip()) < 30]
    html = [c for c in chunks if "<" in c["text"] or "&amp;" in c["text"]]
    short = [c for c in chunks if len(c["text"]) < 80]

    print(f"  Empty/near-empty chunks : {len(empty)}")
    print(f"  Chunks with HTML        : {len(html)}")
    print(f"  Very short chunks (<80) : {len(short)}")

    if empty:
        print("\n  Sample empty chunk IDs:", [c["chunk_id"] for c in empty[:3]])
    if html:
        print("\n  Sample HTML chunk IDs:", [c["chunk_id"] for c in html[:3]])


if __name__ == "__main__":
    inspect_chunks()
