from pathlib import Path
from typing import Dict, Any, List
from src.chunking import extract_pdf_pages, chunk_document_pages
from src.vector_store import vector_store

def ingest_pdf_file(pdf_path: Path) -> Dict[str, Any]:
    """
    Ingests a single PDF file, extracts page text, chunks it, and indexes it into Qdrant.
    """
    doc_id = pdf_path.stem.lower()
    doc_title = pdf_path.stem.replace("_", " ")

    pages = extract_pdf_pages(pdf_path)
    chunks = chunk_document_pages(
        doc_id=doc_id,
        doc_title=doc_title,
        pages_data=pages
    )
    
    vector_store.upsert_chunks(chunks)
    return {
        "document_id": doc_id,
        "title": doc_title,
        "page_count": len(pages),
        "chunk_count": len(chunks)
    }

def ingest_directory(directory_path: Path) -> Dict[str, Any]:
    """
    Ingests all PDF files in a given directory into Qdrant.
    """
    pdf_files = list(directory_path.glob("*.pdf"))
    total_chunks = 0
    results = []

    for pdf in pdf_files:
        info = ingest_pdf_file(pdf)
        total_chunks += info["chunk_count"]
        results.append(info)

    return {
        "status": "success",
        "documents_indexed": len(results),
        "chunks_created": total_chunks,
        "documents": results
    }
