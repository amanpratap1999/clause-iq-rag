from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class Citation(BaseModel):
    document_name: str = Field(..., description="Name of the source document")
    page_number: int = Field(..., description="Exact 1-indexed page number in the source PDF")
    clause: str = Field(..., description="Section or clause heading")
    snippet: str = Field(..., description="Extracted text span supporting the answer")
    score: float = Field(..., description="Vector retrieval similarity score")

    model_config = ConfigDict(from_attributes=True)

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User question about policies or contracts")
    top_k: int = Field(default=4, ge=1, le=10, description="Number of relevant chunks to retrieve")
    document_filter: Optional[str] = Field(None, description="Optional document name filter")

class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    latency_ms: float
    mode: str

    model_config = ConfigDict(from_attributes=True)

class DocumentInfo(BaseModel):
    document_id: str
    title: str
    page_count: int
    chunk_count: int

    model_config = ConfigDict(from_attributes=True)

class DocumentListResponse(BaseModel):
    total_documents: int
    total_chunks: int
    documents: List[DocumentInfo]

class IngestResponse(BaseModel):
    status: str
    documents_indexed: int
    chunks_created: int

class HealthResponse(BaseModel):
    status: str
    vector_db: str
    collection_name: str
    total_chunks: int
    llm_mode: str
    version: str
