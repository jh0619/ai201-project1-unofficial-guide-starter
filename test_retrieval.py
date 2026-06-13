"""
test_retrieval.py — Test retrieval quality against evaluation plan questions.

Usage:
    python test_retrieval.py

Run this AFTER retrieval.py has built the vector store (chroma_db/ exists).
Prints top-k results with distance scores for each test question so you can
manually check: are these chunks actually relevant?
"""

from retrieval import get_collection, get_embedding_model, query, detect_company

# Pulled from planning.md Evaluation Plan
TEST_QUESTIONS = [
    "What is the full interview format for Bloomberg new grad SWE, and how many rounds are there?",
    "What types of coding questions appear in Google L3 new grad interviews, and what is the difficulty level?",
    "What does the Amazon new grad interview process consist of at the assessment stage?",
]


def run_tests(k: int = 5):
    print("Loading embedding model and vector store...")
    model = get_embedding_model()
    collection = get_collection()
    print(f"Vector store has {collection.count()} chunks\n")

    for i, question in enumerate(TEST_QUESTIONS, 1):
        detected = detect_company(question)
        filter_note = f"[company filter: {detected}]" if detected else "[no filter]"
        print("=" * 70)
        print(f"TEST QUESTION {i}: {question}")
        print(filter_note)
        print("=" * 70)

        results = query(question, collection, model, k=k)

        for rank, r in enumerate(results, 1):
            flag = ""
            if r["distance"] > 0.6:
                flag = "  ⚠️  WEAK MATCH (distance > 0.6)"
            elif r["distance"] > 0.5:
                flag = "  ⚠️  borderline (distance > 0.5)"

            print(f"\n  Rank {rank} | distance={r['distance']:.3f}{flag}")
            print(f"  Source: {r['company']} / {r['source']} ({r['filename']})")
            print(f"  URL: {r['url']}")
            print(f"  Text: {r['text'][:300]}")
        print()


if __name__ == "__main__":
    run_tests(k=5)
