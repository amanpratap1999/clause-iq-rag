import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.schemas import (
    QueryRequest,
    QueryResponse,
    DocumentListResponse,
    IngestResponse,
    HealthResponse
)
from src.vector_store import vector_store
from src.rag_pipeline import synthesize_answer
from src.ingest import ingest_directory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("policy_rag")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    count = vector_store.count()
    logger.info(f"Qdrant collection '{settings.QDRANT_COLLECTION_NAME}' loaded with {count} chunks")
    
    if count == 0:
        sample_pdf_dir = Path(__file__).resolve().parent.parent / "sample_docs" / "pdf_files"
        if sample_pdf_dir.exists() and list(sample_pdf_dir.glob("*.pdf")):
            logger.info("Auto-indexing sample PDF corpus into Qdrant...")
            res = ingest_directory(sample_pdf_dir)
            logger.info(f"Auto-indexed {res['documents_indexed']} documents ({res['chunks_created']} chunks)")
    yield

app = FastAPI(
    title="Contract & Policy Q&A Assistant (RAG)",
    description="Production-grade RAG service providing exact page-level and clause-level citations across policy and contract documents.",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please consult logs."}
    )

@app.get("/", include_in_schema=False)
def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Policy & Contract Q&A Assistant API"}

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    points_count = vector_store.count()
    return HealthResponse(
        status="ok",
        vector_db="qdrant-embedded",
        collection_name=settings.QDRANT_COLLECTION_NAME,
        total_chunks=points_count,
        llm_mode="mock" if settings.MOCK_LLM else "live",
        version="0.1.0"
    )

@app.post("/documents/ingest", response_model=IngestResponse, tags=["Documents"])
def ingest_documents():
    """
    Ingests sample PDF contracts and policies from the sample_docs directory into Qdrant.
    """
    sample_pdf_dir = Path(__file__).resolve().parent.parent / "sample_docs" / "pdf_files"
    if not sample_pdf_dir.exists():
        raise HTTPException(status_code=404, detail="Sample PDF directory not found")
        
    res = ingest_directory(sample_pdf_dir)
    return IngestResponse(
        status="success",
        documents_indexed=res["documents_indexed"],
        chunks_created=res["chunks_created"]
    )

@app.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
def list_documents():
    """
    Lists all indexed documents with page counts and chunk statistics.
    """
    docs = vector_store.get_all_documents()
    total_chunks = sum(d["chunk_count"] for d in docs)
    return DocumentListResponse(
        total_documents=len(docs),
        total_chunks=total_chunks,
        documents=docs
    )

@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def query_policies(payload: QueryRequest):
    """
    Ask questions in plain English and receive answers backed by exact page and clause citations.
    """
    logger.info(f"RAG query received: '{payload.question}'")
    response = await synthesize_answer(
        question=payload.question,
        top_k=payload.top_k,
        doc_filter=payload.document_filter
    )
    return response
