# Build Log — Project 1: Contract & Policy Q&A Assistant (RAG)

## Status: Done

### Phase Checklist
- [x] **Phase 1: Discovery & Architecture** (Chunking strategy, citation schema, embedded Qdrant design, ADRs)
- [x] **Phase 2: MVP** (Sample PDF generation, ingestion pipeline, vector retrieval, citation-backed Q&A)
- [x] **Phase 3: Integration** (Full API routes, document management, interactive web chat UI)
- [x] **Phase 4: Evaluation** (24-question benchmark, retrieval hit-rate, answer faithfulness, `docs/eval-results.md`)
- [x] **Phase 5: Deployment** (Local Windows runners, Docker Compose, `/health` endpoint, security audit)
- [x] **Phase 6: Documentation** (`README.md`, `ARCHITECTURE.md` with "How Retrieval Works", DoD sign-off)

---

## Project 1 — Contract & Policy Q&A Assistant
Status: done
DoD checklist:
- All 6 phases complete, in order: PASS
- Local runner boots cleanly / healthcheck verified: PASS
- Test suite green (4/4 unit & integration tests): PASS
- Eval set run (24 legal/policy questions): PASS (Retrieval Page Hit Rate: 91.7%, Answer Faithfulness: 83.3%, Citation Validity: 100.0%, Latency: 3.73ms)
- Security pass run (secrets gitignored, raw stack traces suppressed): PASS
- README.md & ARCHITECTURE.md complete and accurate: PASS
Deviations from spec (if any) + why:
- Used embedded disk-backed Qdrant instead of Docker container per user instruction. Preserved Dockerfile and docker-compose.yml for production deployments. Detailed in [DECISIONS.md](file:///c:/Users/Prakhar%20Singh/Desktop/AI_portfolio_projects/project-1-policy-rag/DECISIONS.md).
