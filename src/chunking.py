import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader

def extract_pdf_pages(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extracts text from each page of a PDF document while preserving physical 1-indexed page numbers.
    """
    reader = PdfReader(str(pdf_path))
    pages_data = []
    
    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        text = page.extract_text() or ""
        pages_data.append({
            "page_number": page_num,
            "text": text.strip()
        })
        
    return pages_data

def chunk_document_pages(
    doc_id: str,
    doc_title: str,
    pages_data: List[Dict[str, Any]],
    chunk_size: int = 500,
    overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Splits document pages into overlapping text chunks strictly within individual page boundaries.
    Preserves section/clause headings as chunk context headers.
    """
    chunks = []
    clause_regex = re.compile(r"^(Section\s+\d+(?:\.\d+)*:?\s*[^.\n]+)", re.MULTILINE | re.IGNORECASE)

    for page_info in pages_data:
        page_num = page_info["page_number"]
        page_text = page_info["text"]
        if not page_text:
            continue

        # Detect clauses on this page
        clauses = []
        matches = list(clause_regex.finditer(page_text))
        if matches:
            for i, m in enumerate(matches):
                start = m.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(page_text)
                clause_header = m.group(1).strip()
                clause_body = page_text[start:end].strip()
                clauses.append((clause_header, clause_body))
        else:
            clauses.append(("General Provisions", page_text))

        # Chunk each clause within the page
        for clause_idx, (clause_header, clause_body) in enumerate(clauses):
            # Clean text
            body_clean = re.sub(r"\s+", " ", clause_body).strip()
            
            # If clause fits in one chunk
            if len(body_clean) <= chunk_size:
                chunks.append({
                    "id": f"{doc_id}_p{page_num}_cl{clause_idx}_0",
                    "doc_id": doc_id,
                    "doc_title": doc_title,
                    "page_number": page_num,
                    "clause_title": clause_header,
                    "text": body_clean
                })
            else:
                # Sliding window chunking
                start_char = 0
                sub_idx = 0
                while start_char < len(body_clean):
                    end_char = min(start_char + chunk_size, len(body_clean))
                    chunk_text = body_clean[start_char:end_char].strip()
                    if chunk_text:
                        chunks.append({
                            "id": f"{doc_id}_p{page_num}_cl{clause_idx}_{sub_idx}",
                            "doc_id": doc_id,
                            "doc_title": doc_title,
                            "page_number": page_num,
                            "clause_title": clause_header,
                            "text": f"[{clause_header}] {chunk_text}"
                        })
                        sub_idx += 1
                    start_char += chunk_size - overlap
                    if end_char == len(body_clean):
                        break

    return chunks
