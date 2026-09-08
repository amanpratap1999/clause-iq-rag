# Architectural Decisions Record (ADR) — Project 1: Contract & Policy Q&A Assistant

## ADR 001: Page-Aware Chunking Strategy
- **Context:** RAG citation reliability breaks when chunks span multiple pages or lose their clause context. Staff asking questions about contracts need to verify the exact page and clause cited.
- **Decision:** Implement page-boundary-enforced, header-aware chunking:
  1. Documents are first extracted page by page using `pypdf`.
  2. Section and clause headings (e.g., `Section 3.1: Termination for Cause`) are detected via regex heuristics and prepended to chunks as context headers.
  3. Sliding window chunk size of 500 characters with 100 characters overlap is applied **strictly within individual pages**. A chunk NEVER crosses page boundaries.
- **Tradeoff & Mitigation:** Slightly smaller context chunks at the bottom of pages, but guarantees 100% citation accuracy to the physical source page.

## ADR 002: Structured Citation Format & Verification
- **Context:** Free-form citations in LLM text can be vague (e.g. "according to policy") or hallucinated.
- **Decision:**
  - Every chunk in Qdrant contains rich payload metadata: `{doc_id, doc_title, page_number, clause_title, text}`.
  - LLM prompts demand explicit bracketed citations: `[Doc Title, Page X, Clause Y]`.
  - The API response layer cross-references bracketed citations against the actual retrieved candidate chunks, returning both the synthesized text and a structured list of verified `Citation` objects with exact source snippets.
- **Tradeoff:** Minimal post-processing overhead in exchange for guaranteed citation traceability.

## ADR 003: Embedded Qdrant for Local Windows Execution
- **Context:** `AGENT_BUILD_SPEC.md` requires Qdrant. The user instructed a local Windows setup without Docker.
- **Decision:** Use Qdrant's embedded disk-backed mode via `QdrantClient(path="./qdrant_storage")`.
- **Tradeoff & Mitigation:** Eliminates Docker container requirements on Windows while keeping 100% API compatibility with external Qdrant clusters. `docker-compose.yml` is preserved for cloud/containerized deployments.

## ADR 004: Dual-Mode Synthesis & Local Vector Embeddings
- **Context:** The user will supply the LLM API key later.
- **Decision:**
  - Embeddings are generated locally using normalized dense n-gram token vectors or FastEmbed on CPU.
  - When `MOCK_LLM=true` (or no API key), a deterministic extractive synthesizer extracts the most relevant sentence from the top retrieved chunk and formats verified citations.
  - When `MOCK_LLM=false`, live prompts query Groq (`llama-3.3-70b-versatile`) or OpenAI.
- **Tradeoff:** Enables immediate, green test suite and evaluation benchmark runs prior to user API key input.
