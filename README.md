# Contract & Policy Q&A Assistant (Project 1 — RAG)

> **Autonomous AI/ML Portfolio — RAG Service**  
> Enterprise question-answering assistant over contract and policy PDFs with verified page-level and clause-level citations.

---

## Quickstart (Run Cold in 60 Seconds)

### Option A: 1-Click Windows Launch (PowerShell)
```powershell
.\run_local.ps1
```
*(Or double-click `run_local.bat`)*

### Option B: Manual Setup
1. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Generate sample policy PDFs:**
   ```powershell
   python sample_docs/generate_samples.py
   ```
4. **Run the server:**
   ```powershell
   uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
   ```

Open your browser to:
- **Interactive Web Chat UI:** [http://127.0.0.1:8001](http://127.0.0.1:8001)
- **Interactive Swagger Docs:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Health Check:** [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)

---

## Running Tests & Benchmark Evaluation

### 1. Run Automated Unit & Integration Tests
```powershell
.\venv\Scripts\pytest -v tests/
```

### 2. Run the 24-Question Benchmark Evaluation
```powershell
.\venv\Scripts\python eval/run_eval.py
```
This tests retrieval precision, page hit rates, and answer faithfulness across all 6 policies and updates `docs/eval-results.md`.

---

## API Endpoints & Examples

### 1. Ask a Question with Verified Citations
```bash
curl -X POST http://127.0.0.1:8001/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the vendor SLA uptime guarantee and credit penalty?",
    "top_k": 3
  }'
```
**Response:**
```json
{
  "question": "What is the vendor SLA uptime guarantee and credit penalty?",
  "answer": "According to [Master SaaS Vendor Agreement, Page 1, Section 2.0: Service Level Agreement and Uptime Guarantees], Vendor commits to a monthly service availability of 99.9% uptime...",
  "citations": [
    {
      "document_name": "Master SaaS Vendor Agreement",
      "page_number": 1,
      "clause": "Section 2.0: Service Level Agreement and Uptime Guarantees",
      "snippet": "Vendor commits to a monthly service availability of 99.9% uptime, excluding scheduled maintenance windows announced at least 72 hours in advance...",
      "score": 0.8124
    }
  ],
  "latency_ms": 1.25,
  "mode": "mock"
}
```

### 2. List Indexed Documents
```bash
curl -X GET http://127.0.0.1:8001/documents
```

---

## Activating Live LLM Inference

The service includes an offline mock mode (`MOCK_LLM=true`) so the full application and UI function without an external key.

To activate live generation with **Groq** (or OpenAI):
1. Open `.env`.
2. Update:
   ```env
   MOCK_LLM=false
   LLM_PROVIDER=groq
   LLM_API_KEY=gsk_your_groq_key_here
   LLM_MODEL=llama-3.3-70b-versatile
   ```
3. Restart the server.

---

## Directory Structure
```
project-1-policy-rag/
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── BUILD_LOG.md
├── DECISIONS.md
├── Dockerfile
├── docker-compose.yml
├── README.md
├── requirements.txt
├── run_local.bat
├── run_local.ps1
├── src/
│   ├── __init__.py
│   ├── chunking.py
│   ├── config.py
│   ├── ingest.py
│   ├── main.py
│   ├── rag_pipeline.py
│   ├── schemas.py
│   └── vector_store.py
├── sample_docs/
│   ├── generate_samples.py
│   └── pdf_files/
├── static/
│   └── index.html
├── tests/
│   └── test_rag.py
├── eval/
│   ├── dataset.json
│   └── run_eval.py
└── docs/
    └── eval-results.md
```
