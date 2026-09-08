import re
import time
import logging
from typing import List, Dict, Any, Optional
import httpx
from src.config import settings
from src.schemas import Citation, QueryResponse
from src.vector_store import vector_store

logger = logging.getLogger(__name__)

SYSTEM_RAG_PROMPT = """You are a precise corporate legal and policy compliance assistant.
Answer the user's question based EXCLUSIVELY on the provided document excerpts.
Every statement or fact in your answer MUST be accompanied by an inline citation to its source in the format: [Document Title, Page X, Clause Y].
Do not fabricate facts or speculate beyond the provided excerpts. If the information is not contained in the context, explicitly state that the documents do not cover it.
"""

def extract_best_answer_sentence(query: str, text: str) -> str:
    """
    Heuristic to extract the most relevant sentence from context for mock/offline synthesis.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    query_words = set(re.sub(r"[^\w\s]", "", query.lower()).split())
    
    best_sent = ""
    best_overlap = -1
    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        words = set(re.sub(r"[^\w\s]", "", s_clean.lower()).split())
        overlap = len(words.intersection(query_words))
        if overlap > best_overlap:
            best_overlap = overlap
            best_sent = s_clean
            
    return best_sent if best_sent else (sentences[0] if sentences else text)

async def synthesize_answer(
    question: str,
    top_k: int = 4,
    doc_filter: Optional[str] = None
) -> QueryResponse:
    start_time = time.perf_counter()
    
    # 1. Retrieve top-k relevant chunks from Qdrant
    hits = vector_store.search(query=question, top_k=top_k, doc_filter=doc_filter)
    
    if not hits:
        latency = (time.perf_counter() - start_time) * 1000
        return QueryResponse(
            question=question,
            answer="No relevant documents or policy clauses were found matching your query.",
            citations=[],
            latency_ms=round(latency, 2),
            mode="mock" if settings.MOCK_LLM else "live"
        )

    # 2. Build structured citations
    citations: List[Citation] = []
    context_blocks: List[str] = []
    
    for hit in hits:
        snippet_text = hit["text"]
        # Strip header prefix if present for cleaner snippet
        snippet_clean = re.sub(r"^\[.*?\]\s*", "", snippet_text)
        
        citations.append(
            Citation(
                document_name=hit["doc_title"],
                page_number=int(hit["page_number"]),
                clause=hit["clause_title"],
                snippet=snippet_clean[:280] + ("..." if len(snippet_clean) > 280 else ""),
                score=hit["score"]
            )
        )
        
        context_blocks.append(
            f"Source [{hit['doc_title']}, Page {hit['page_number']}, {hit['clause_title']}]:\n{hit['text']}"
        )

    context_str = "\n\n".join(context_blocks)

    # 3. Answer synthesis
    if settings.MOCK_LLM or not settings.LLM_API_KEY:
        from src.vector_store import STOPWORDS
        raw_words = re.findall(r"\b[\w$%.]+\b", question.lower())
        query_words = {w for w in raw_words if w not in STOPWORDS}
        if not query_words:
            query_words = set(raw_words)

        best_hit = hits[0]
        best_overlap = -1
        best_sentence = ""

        for h in hits:
            sent = extract_best_answer_sentence(question, h["text"])
            sent_words = set(re.findall(r"\b[\w$%.]+\b", sent.lower()))
            overlap = len(sent_words.intersection(query_words))
            if overlap > best_overlap:
                best_overlap = overlap
                best_hit = h
                best_sentence = sent

        if not best_sentence:
            best_sentence = extract_best_answer_sentence(question, best_hit["text"])

        answer_text = (
            f"According to [{best_hit['doc_title']}, Page {best_hit['page_number']}, {best_hit['clause_title']}], "
            f"{best_sentence}"
        )
    else:
        # Live LLM Inference via Groq / OpenAI
        base_url = "https://api.groq.com/openai/v1/chat/completions" if settings.LLM_PROVIDER == "groq" else "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        user_message = f"Excerpts:\n{context_str}\n\nQuestion: {question}\n\nProvide a direct, factual answer with inline citations:"
        payload = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_RAG_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.1
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(base_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                answer_text = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Live LLM call failed: {e}. Falling back to deterministic extractive synthesis.")
            top_hit = hits[0]
            extracted_sentence = extract_best_answer_sentence(question, top_hit["text"])
            answer_text = (
                f"According to [{top_hit['doc_title']}, Page {top_hit['page_number']}, {top_hit['clause_title']}], "
                f"{extracted_sentence}"
            )

    latency = (time.perf_counter() - start_time) * 1000
    return QueryResponse(
        question=question,
        answer=answer_text,
        citations=citations,
        latency_ms=round(latency, 2),
        mode="mock" if settings.MOCK_LLM else "live"
    )
