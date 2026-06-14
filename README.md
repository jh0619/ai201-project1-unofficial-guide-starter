# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

This system covers new grad software engineering interview experiences at four
companies: Bloomberg, Apple, Google, and Amazon — including interview format,
number of rounds, coding question types and difficulty, and behavioral/assessment
stages.

This knowledge is valuable because official company career pages describe their
interview processes only generically. The real signal — how many rounds there
actually are, which LeetCode topics and difficulty to expect, what the online
assessment contains, whether system design comes up for new grads — lives
scattered across Blind, Reddit, LeetCode Discuss, and Glassdoor. There is no
single searchable place to ask "what does the Amazon new grad assessment actually
consist of?" or "does Bloomberg new grad include system design?" This system
consolidates that candidate-generated knowledge into one queryable, cited
interface.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| #   | Source    | Description                                    | URL or location                                                                                  |
| --- | --------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 1   | Blind     | "Bloomberg interview process"                  | https://www.teamblind.com/post/bloomberg-interview-process-ymx04b5i                              |
| 2   | Blind     | "Bloomberg new grad interview"                 | https://www.teamblind.com/post/bloomberg-new-grad-interview-dvxpnaes                             |
| 3   | Blind     | "Bloomberg Interview Process"                  | https://www.teamblind.com/post/bloomberg-interview-process-jypvloej                              |
| 4   | Reddit    | "Apple SWE New Grad Technical Interview"       | https://www.reddit.com/r/csMajors/comments/1ohnn13/apple_swe_new_grad_technical_interview/       |
| 5   | Reddit    | "Apple New Grad Interview Expectations?"       | https://www.reddit.com/r/FAANGrecruiting/comments/1otr1bf/apple_new_grad_interview_expectations/ |
| 6   | Reddit    | "Apple new grad SWE role"                      | https://www.reddit.com/r/leetcode/comments/1m7j1pm/apple_new_grad_swe_role/                      |
| 7   | Reddit    | "Google New Grad 2026 – Interview Experience"  | https://www.reddit.com/r/leetcode/comments/1tloebj/google_new_grad_2026_interview_experience/    |
| 8   | Reddit    | "Google New Grad Interview Experience"         | https://www.reddit.com/r/leetcode/comments/1p1gi4t/google_new_grad_interview_experience/         |
| 9   | Glassdoor | "Software Engineer Graduate Interview(Amazon)" | https://www.glassdoor.com/Interview/Amazon-Interview-E6036-RVW103632134.htm                      |
| 10  | Glassdoor | "Graduate Software Engineer Interview(Amazon)" | https://www.glassdoor.com/Interview/Amazon-Interview-E6036-RVW104015185.htm                      |
| 11  | Glassdoor | "Graduate Software Engineer Interview(Amazon)" | https://www.glassdoor.com/Interview/Amazon-Interview-E6036-RVW104302774.htm                      |
| 12  | Reddit    | "Google SWE New Grad R1 experience"            | https://www.reddit.com/r/leetcode/comments/1si4bae/google_swe_new_grad_r1_experience/            |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
400 characters

**Overlap:**
80 characters

**Why these choices fit your documents:**
These documents are forum posts and reviews — short, opinion-dense paragraphs
where a single sentence often carries the key fact (e.g. "3 technical rounds, all
LC mediums, no system design"). A large chunk would bundle unrelated facts and
dilute the semantic signal, so a narrow query matches the right company but the
wrong topic. 400 characters is roughly 2–4 sentences, which captures one coherent
idea — a round description, a piece of advice, or a topic warning. The 80-character
overlap (~half a sentence) keeps facts that sit on a chunk boundary retrievable in
the adjacent chunk, so a round description that starts at the end of one chunk
still appears in the next. The chunker also snaps to sentence boundaries where
possible and filters out fragments shorter than 80 characters.

**Final chunk count:**
78 chunks across 12 documents (inside the healthy
50–2000 range)

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2 via sentence-transformers, producing
384-dimensional embeddings. Stored in ChromaDB with cosine distance. It runs
locally with no API key and no rate limits, which makes it practical and fully
reproducible for a free student project.

**Production tradeoff reflection:**
If deploying for real users with cost no object, I would weigh:
Context length: MiniLM truncates at 256 tokens. A longer-context model
(e.g. OpenAI text-embedding-3-large) would embed full-length interview guides
without information loss.
Domain accuracy: MiniLM is general-purpose and not tuned on tech-career
text. A fine-tuned or domain-specific model would better embed jargon like
"Power Day," "team matching," "Googleyness," or "Bloomberg tagged."
Latency vs. accuracy: local inference is fast but less accurate than
API-hosted embeddings; at ~$0.0001/query the accuracy gain is likely worth it
in production.
Multilingual support: not needed here (all English), but a global student
audience would call for a multilingual model such as
paraphrase-multilingual-MiniLM-L12-v2.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The LLM (Groq llama-3.3-70b-versatile, temperature 0.1) is given a system
prompt with strict rules: answer using ONLY information in the provided context;
do not use outside or general knowledge about these companies; if the context is
insufficient, respond with exactly "I don't have enough information on that.";
and never invent round counts, numbers, or company specifics not stated in the
context. Each retrieved chunk is inserted into the prompt labeled with its source
filename and company, so every fact the model uses is tied to a specific
document. The low temperature keeps the model close to the retrieved wording
rather than paraphrasing from its own knowledge.

**How source attribution is surfaced in the response:**
Attribution is generated programmatically in Python, not by the LLM. After
retrieval, the ask() function builds the source list directly from the
retrieved chunks' metadata (deduplicated by filename, with the original URL
attached). This guarantees citations are deterministic and reflect exactly what
was retrieved — the model cannot hallucinate a source it didn't use. If the model
declines to answer ("I don't have enough information"), the source list is
suppressed so the refusal isn't falsely attributed to documents.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

All 5 questions were run end-to-end via evaluate.py (retrieval top-k=5, grounded
generation).

| #   | Question                                                                            | Expected answer                                                                      | System response (summarized)                                                                                    | Retrieval quality                                             | Response accuracy  |
| --- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------ |
| 1   | What is the full interview format for Bloomberg new grad SWE, and how many rounds?  | Phone screen → 2–3 technical → 1–2 non-technical onsite (behavioral + EM); ~5 rounds | "I don't have enough information on that."                                                                      | Relevant (5/5 Bloomberg, top dist 0.331)                      | Inaccurate         |
| 2   | Does the Bloomberg new grad interview include system design?                        | Mixed: most say no (all-LC), but one says "everyone gets it"                         | System design may appear in a later EM round; not confirmed for initial rounds                                  | Relevant (5/5 Bloomberg, top dist 0.353)                      | Partially accurate |
| 3   | What coding question types and difficulty appear in Google L3 new grad interviews?  | Graph (incl. hard), arrays, sliding window, hash maps; easy → medium/hard            | Listed arrays, sliding window, hash maps, pointers; easy/medium; noted corpus lacks "L3" label                  | Relevant (5/5 Google, top dist 0.393)                         | Partially accurate |
| 4   | What does the Amazon new grad assessment stage consist of?                          | Online HackerRank (1 easy + 1 medium-hard) + Work Style Assessment / behavioral      | Online assessment + HackerRank (1 easy, 1 med-hard) + Work Style Assessment + behavioral + situational judgment | Relevant (5/5 Amazon, top dist 0.403)                         | Accurate           |
| 5   | Across these companies, what is the most common advice for new grad SWE interviews? | Synthesized theme: grind LC mediums (esp. tagged), narrate your approach clearly     | "I don't have enough information on that."                                                                      | Off-target (top 5 = Apple ×3, Google ×2; no Bloomberg/Amazon) | Inaccurate         |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"Across these companies, what is the most common piece
of advice candidates give for new grad SWE interviews?"

**What the system returned:**
"I don't have enough information on that." The top 5
retrieved chunks were all Apple (×3) and Google (×2) — zero Bloomberg, zero
Amazon — so a genuine "across these companies" synthesis was impossible.

**Root cause (tied to a specific pipeline stage):**
This query names
no company, so the company metadata filter does not fire and search is global. The
phrasing ("advice ... new grad SWE interviews") embeds closest to the Apple/Google
question posts, which literally contain "new grad SWE" and advice-style
language. With top-k=5, all five nearest neighbors came from just two companies,
so the context window never contained Bloomberg or Amazon material. Retrieval is
behaving exactly as designed (pure nearest-neighbor), but semantic
nearest-neighbor search does not guarantee source diversity, which a
cross-company synthesis question fundamentally requires.

**What you would change to fix it:**
or synthesis questions, detect
multi-company intent and retrieve top-k per company, then merge — guaranteeing
each company is represented; or raise top-k substantially so more sources enter
the context.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The Chunking Strategy section of planning.md forced me to commit to 400/80
before writing any code, with a written rationale tied to the document structure
(short, opinion-dense forum posts). When retrieval later returned the right
company but loosely related content, I had a documented baseline to reason from
instead of tuning blindly. It let me conclude that my failures were about corpus
composition and chunk granularity, not about the chunk size being wrong — a
diagnosis I could only make because the spec recorded my original reasoning.

**One way your implementation diverged from the spec, and why:**
The spec planned 10 documents with Google sourced from LeetCode Discuss. In
practice those LeetCode posts were mostly low-signal — "team matching" wait-time
chatter and congratulatory comments — and Google retrieval distances sat above
0.5. Driven by real retrieval evidence from Milestone 4, I diverged by replacing the
weak LeetCode Google posts with higher-quality Google experience posts from Reddit
(ending at 12 documents, with 3 Google Reddit threads) and by implementing company
metadata filtering, which I had originally listed only as a stretch feature. Both
changes were prompted by what the diagnostics showed, not by the original plan.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- _What I gave the AI:_
  My Milestone 4 retrieval results showing that the Google
  L3 question returned Apple and Bloomberg chunks instead of Google, plus my
  ChromaDB schema. I asked it to help me figure out why and how to fix it.
- _What it produced:_
  A diagnostic script that ranked where Google chunks fell in
  a top-20 search and printed their full text, which revealed Google chunks ranked
  far below the cutoff and that the corpus was mostly noise. It then proposed three
  fixes: metadata filtering, larger chunks, or accepting it as a failure case.
- _What I changed or overrode:_
  I directed it specifically toward metadata
  filtering rather than the other options, and then independently decided to also
  improve the corpus by adding better Google posts — a step the AI hadn't
  prioritized — because the diagnostic made clear the root cause was data quality,
  not just ranking order.

**Instance 2**

- _What I gave the AI:_
  My grounding requirement from Milestone 5 (answers from
  retrieved context only, with source attribution) and asked it to implement the
  generation function.
- _What it produced:_
  A first version that instructed the LLM to cite its sources
  inside its own generated text.
- _What I changed or overrode:_
  I overrode this because the Milestone 5 requirement
  is that attribution be programmatically guaranteed, not LLM-generated. I
  directed it to build the source list in Python from the retrieved chunks'
  metadata (dedup by filename, attach URL) and to suppress sources when the model
  declines to answer. This made citations deterministic and stopped the model from
  hallucinating a source it didn't actually use.
