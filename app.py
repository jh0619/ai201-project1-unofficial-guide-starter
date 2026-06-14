"""
app.py — Gradio web interface for The Unofficial Guide.

Usage:
    python app.py
    Then open http://localhost:7860 in your browser.
"""

import gradio as gr

from generate import ask


EXAMPLE_QUESTIONS = [
    "What is the interview format for Bloomberg new grad SWE?",
    "What types of coding questions appear in Google L3 new grad interviews?",
    "What does the Amazon new grad assessment stage consist of?",
    "What should I expect in an Apple new grad coding screen?",
]


def handle_query(question: str):
    if not question or not question.strip():
        return "Please enter a question.", ""

    result = ask(question)

    answer = result["answer"]
    if result["sources"]:
        sources = "\n".join(f"• {s}" for s in result["sources"])
    else:
        sources = "(no sources — the system did not find relevant documents)"

    return answer, sources


with gr.Blocks(title="The Unofficial Guide — SWE Interview RAG") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about new grad SWE interviews at **Bloomberg, Apple, Google, or Amazon**. "
        "Answers are grounded in real candidate experience posts from Blind, Reddit, "
        "LeetCode, and Glassdoor — with sources cited."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Does Bloomberg new grad include system design?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=inp)


if __name__ == "__main__":
    demo.launch()
