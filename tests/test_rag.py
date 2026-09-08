import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.chunking import chunk_document_pages
from src.vector_store import vector_store

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["vector_db"] == "qdrant-embedded"
    assert "total_chunks" in data
    assert "llm_mode" in data

def test_chunking_page_boundary_enforcement():
    pages = [
        {"page_number": 1, "text": "Section 1.0: First Page\nThis is text exclusively on the first physical page."},
        {"page_number": 2, "text": "Section 2.0: Second Page\nThis is text exclusively on the second physical page."}
    ]
    chunks = chunk_document_pages("test_doc", "Test Document", pages, chunk_size=300, overlap=50)
    
    assert len(chunks) >= 2
    for c in chunks:
        if "first physical page" in c["text"].lower():
            assert c["page_number"] == 1
        if "second physical page" in c["text"].lower():
            assert c["page_number"] == 2

def test_ingest_and_query_pipeline(client):
    # Upsert test chunks directly
    test_chunks = [
        {
            "id": "agreement_p1_c0",
            "doc_id": "vendor_agreement",
            "doc_title": "Master Vendor Agreement",
            "page_number": 1,
            "clause_title": "Section 2.0: Uptime SLA",
            "text": "Vendor commits to a monthly service availability of 99.9% uptime, excluding scheduled maintenance windows."
        },
        {
            "id": "policy_p1_c0",
            "doc_id": "expense_policy",
            "doc_title": "Travel and Expense Policy",
            "page_number": 1,
            "clause_title": "Section 2.0: Daily Meals",
            "text": "The company reimburses business meals up to a maximum per diem of $75 per day for domestic travel."
        }
    ]
    vector_store.upsert_chunks(test_chunks)

    # Query about uptime
    payload = {"question": "What is the vendor uptime guarantee?", "top_k": 2}
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "99.9%" in data["answer"] or len(data["citations"]) > 0
    assert len(data["citations"]) >= 1
    
    top_citation = data["citations"][0]
    assert "document_name" in top_citation
    assert top_citation["page_number"] >= 1
    assert "clause" in top_citation
    assert "snippet" in top_citation

def test_query_validation(client):
    # Too short question
    response = client.post("/query", json={"question": "a"})
    assert response.status_code == 422
