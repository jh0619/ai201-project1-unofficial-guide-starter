"""
evaluate.py — Run all 5 evaluation questions end-to-end and dump results.
Milestone 6: The Unofficial Guide (New Grad SWE Interview RAG)

Usage:
    python evaluate.py

Prints, for each question:
  - the question
  - the retrieved chunks (source + distance) — what retrieval returned
  - the generated answer
  - the programmatic source list

Copy this output into your README evaluation table and add your accuracy
judgment (accurate / partially accurate / inaccurate) by hand.
"""

from generate import ask
from retrieval import detect_company


# The 5 evaluation questions from planning.md
EVAL_QUESTIONS = [
    "What is the full interview format for Bloomberg new grad SWE, and how many rounds are there?",
    "Does the Bloomberg new grad interview include system design?",
    "What types of coding questions appear in Google L3 new grad interviews, and what is the difficulty level?",
    "What does the Amazon new grad interview process consist of at the assessment stage?",
    "Across these companies, what is the most common piece of advice candidates give for new grad SWE interviews?",
]


def run_eval():
    for i, question in enumerate(EVAL_QUESTIONS, 1):
        detected = detect_company(question)
        filter_note = f"company filter: {detected}" if detected else "no filter (global search)"

        print("=" * 75)
        print(f"QUESTION {i}: {question}")
        print(f"[{filter_note}]")
        print("=" * 75)

        result = ask(question, k=5)

        print("\n--- RETRIEVED CHUNKS ---")
        for rank, c in enumerate(result["chunks"], 1):
            print(f"  {rank}. [{c['company']}/{c['source']}] dist={c['distance']:.3f} "
                  f"| {c['filename']}")
            print(f"     {c['text'][:120].strip()}...")

        print("\n--- GENERATED ANSWER ---")
        print(result["answer"])

        print("\n--- SOURCES (programmatic) ---")
        if result["sources"]:
            for s in result["sources"]:
                print(f"  • {s}")
        else:
            print("  (none — system declined to answer)")

        print("\n")


if __name__ == "__main__":
    run_eval()
