# System Architecture — Contract & Policy Q&A Assistant (RAG)

## 1. Executive Summary

The **Contract & Policy Q&A Assistant** is an enterprise-grade Retrieval-Augmented Generation (RAG) system engineered to eliminate hallucination in high-stakes legal, HR, and compliance document queries. Unlike conventional naive RAG systems that quote documents without verifiable provenance, this system guarantees that **every extracted answer is paired with an exact document title, physical page number, and clause heading**.

---

## 2. Ingestion Pipeline & Chunking Design

```
+---------------------------------------------------------------------------------+
|                                 Raw PDF Ingestion                               |
|              (Remote Work, Master SaaS, Security Standards, etc.)               |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                    Page Extraction & Boundary Guard (pypdf)                     |
|  - Physical page boundaries are strictly recorded (1-indexed).                  |
|  - Text is grouped by page: Chunks NEVER cross page boundaries.                 |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                 Clause-Aware Chunking (src/chunking.py)                         |
|  - Regex identifies section/clause headers (e.g. 'Section 2.0: Uptime SLA').    |
|  - Header is prepended to chunk text for contextual vectorization.             |
|  - 500-character window with 100-character overlap within the page.             |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                           Vector Indexing (Qdrant)                              |
|  - 128-dim normalized dense vector per chunk.                                   |
|  - Rich Payload: {doc_title, page_number, clause_title, text}.                 |
+---------------------------------------------------------------------------------+
```

---

## 3. How Retrieval Works (Client-Facing Technical Breakdown)

When a user or client asks: *"How does your retrieval system actually find the right answer without hallucinating?"*, the system relies on a four-stage process:

1. **Query Vectorization:**  
   The natural-language question (e.g., *"What credit do we get if vendor uptime is 99.2%?"*) is converted into a normalized dense vector representing both semantic concepts and critical key tokens.
2. **Nearest-Neighbor Cosine Search:**  
   Qdrant computes the cosine distance against all indexed document vectors:
   $$\text{similarity}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|}$$
   Because vectors are $L_2$-normalized, this computation is an ultra-fast dot product.
3. **Metadata-Enriched Candidate Scoring:**  
   The top-$k$ nearest chunks are retrieved with their full metadata payloads (`doc_title`, `page_number`, `clause_title`).
4. **Guaranteed Provenance Citation:**  
   Because chunks never span multiple pages, when chunk $C$ ranks in the top candidates, its page number ($P$) is guaranteed to be the exact physical page in the PDF where the clause resides.

---

## 4. Synthesis & Citation Verification

- **Dual-Mode Inference:**
  - **Mock / Offline Mode:** Uses deterministic extractive synthesis to extract the most relevant sentence from the top candidate chunk and formats verified bracketed citations (`[Doc Name, Page X, Clause Y]`).
  - **Live LLM Mode:** Uses Groq (`llama-3.3-70b-versatile`) or OpenAI with a temperature of `0.1` and a system prompt requiring that all factual assertions be directly tied to bracketed source citations.
- **Citation Parsing:**
  - The API response layer cross-references bracketed citations and returns structured `Citation` models containing snippet text, page number, and similarity score to feed the frontend's interactive citation cards.

---

## 5. Architectural Decisions & Tradeoffs

| Decision | Alternative Considered | Tradeoff & Rationale |
|---|---|---|
| **Embedded Qdrant on Disk** | Docker Qdrant or Cloud Vector DB | Runs natively on Windows without requiring Docker Desktop, eliminating daemon complexity and external cloud latency. |
| **Page-Bounded Chunking** | Fixed Token Chunking (LangChain default) | Standard token chunking splits text across page breaks, corrupting page citations. Page-bounded chunking guarantees that page numbers are 100% accurate. |
| **Dual-Mode LLM Client** | Live-Only API | Guarantees green tests, automated evaluation, and CI pipelines run offline without consuming paid API quotas. |
