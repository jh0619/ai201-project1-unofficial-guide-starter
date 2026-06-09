# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

New Grad SWE Interview Experiences — covering technical (LeetCode, system design) and behavioral rounds at top companies.
This knowledge is valuable because official company career pages only describe the process generically. The real signal — what topics actually appear, how interviewers evaluate answers, which behavioral themes recur — lives in candidate experience posts scattered across Blind, Reddit, Glassdoor, and LeetCode discuss. There's no single place to search "what does Capital One TDP actually test in system design."

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source    | Description                                    | URL or location                                                                                  |
| --- | --------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 1   | Blind     | "Bloomberg interview process"                  | https://www.teamblind.com/post/bloomberg-interview-process-ymx04b5i                              |
| 2   | Blind     | "Bloomberg new grad interview"                 | https://www.teamblind.com/post/bloomberg-new-grad-interview-dvxpnaes                             |
| 3   | Blind     | "Bloomberg Interview Process"                  | https://www.teamblind.com/post/bloomberg-interview-process-jypvloej                              |
| 4   | Reddit    | "Apple SWE New Grad Technical Interview"       | https://www.reddit.com/r/csMajors/comments/1ohnn13/apple_swe_new_grad_technical_interview/       |
| 5   | Reddit    | "Apple New Grad Interview Expectations?"       | https://www.reddit.com/r/FAANGrecruiting/comments/1otr1bf/apple_new_grad_interview_expectations/ |
| 6   | Reddit    | "Apple new grad SWE role"                      | https://www.reddit.com/r/leetcode/comments/1m7j1pm/apple_new_grad_swe_role/                      |
| 7   | Leetcode  | "Cracked Google - interview experience L3"     | https://leetcode.com/discuss/post/8324412/cracked-google-interview-experience-l3-b-xgeq/         |
| 8   | Leetcode  | "L3 Team matching (Google)"                    | https://leetcode.com/discuss/post/8256291/l3-team-matching-by-anonymous_user-4ouh/               |
| 9   | Glassdoor | "Software Engineer Graduate Interview(Amazon)" | https://www.glassdoor.com/Interview/Amazon-Interview-E6036-RVW103632134.htm                      |
| 10  | Glassdoor | "Graduate Software Engineer Interview(Amazon)" | https://www.glassdoor.com/Interview/Amazon-Interview-E6036-RVW104015185.htm                      |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question | Expected answer |
| --- | -------- | --------------- |
| 1   |          |                 |
| 2   |          |                 |
| 3   |          |                 |
| 4   |          |                 |
| 5   |          |                 |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
