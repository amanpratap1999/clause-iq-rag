import math
import hashlib
import re
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.config import settings

VECTOR_DIM = 256

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "many", "much", "must", "is", "are"
}

def generate_local_embedding(text: str, dim: int = VECTOR_DIM) -> List[float]:
    """
    Computes a deterministic, normalized dense vector embedding using stopword-filtered
    n-grams with term length and uppercase weight amplification.
    """
    raw_tokens = re.findall(r"\b[\w$%.]+\b", text)
    tokens = [t.lower() for t in raw_tokens if t.lower() not in STOPWORDS]
    
    vec = np.zeros(dim, dtype=np.float32)
    if not tokens:
        tokens = [t.lower() for t in raw_tokens]
        if not tokens:
            return vec.tolist()

    features = list(tokens)
    for i in range(len(tokens) - 1):
        features.append(f"{tokens[i]}_{tokens[i+1]}")

    for feat in features:
        h = int(hashlib.md5(feat.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 8) & 1) == 1 else -1.0
        # Boost numbers, acronyms, and specific entities
        weight = 1.0 + math.log(len(feat) + 1.0)
        if any(char.isdigit() or char in "$%" for char in feat):
            weight *= 2.5
        vec[idx] += sign * weight

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
        
    return vec.tolist()

def get_embedding(text: str) -> List[float]:
    return generate_local_embedding(text)

class VectorStore:
    def __init__(self, storage_path: str = settings.QDRANT_STORAGE_PATH, collection_name: str = settings.QDRANT_COLLECTION_NAME):
        self.collection_name = collection_name
        self.client = QdrantClient(path=storage_path)
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=VECTOR_DIM,
                    distance=models.Distance.COSINE
                )
            )

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return

        points = []
        for idx, chunk in enumerate(chunks):
            # Deterministic integer point ID derived from chunk id string
            point_id = int(hashlib.md5(chunk["id"].encode("utf-8")).hexdigest()[:15], 16)
            vector = get_embedding(chunk["text"])
            
            payload = {
                "chunk_id": chunk["id"],
                "doc_id": chunk["doc_id"],
                "doc_title": chunk["doc_title"],
                "page_number": chunk["page_number"],
                "clause_title": chunk["clause_title"],
                "text": chunk["text"]
            }
            
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query: str, top_k: int = 4, doc_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query_vec = get_embedding(query)
        
        query_filter = None
        if doc_filter:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="doc_title",
                        match=models.MatchValue(value=doc_filter)
                    )
                ]
            )

        # qdrant-client v1.8+ supports query_points
        try:
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vec,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True
            ).points
        except Exception:
            # Fallback for search API
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vec,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True
            )

        results = []
        for hit in search_result:
            payload = hit.payload or {}
            results.append({
                "chunk_id": payload.get("chunk_id"),
                "doc_id": payload.get("doc_id"),
                "doc_title": payload.get("doc_title"),
                "page_number": payload.get("page_number"),
                "clause_title": payload.get("clause_title"),
                "text": payload.get("text"),
                "score": round(float(hit.score), 4)
            })
            
        return results

    def count(self) -> int:
        try:
            return self.client.get_collection(self.collection_name).points_count or 0
        except Exception:
            return 0

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Scrolls through collection to list indexed documents.
        """
        records, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=500,
            with_payload=True,
            with_vectors=False
        )
        
        docs: Dict[str, Dict[str, Any]] = {}
        for r in records:
            payload = r.payload or {}
            doc_id = payload.get("doc_id", "unknown")
            if doc_id not in docs:
                docs[doc_id] = {
                    "document_id": doc_id,
                    "title": payload.get("doc_title", "Unknown"),
                    "pages": set(),
                    "chunk_count": 0
                }
            docs[doc_id]["pages"].add(payload.get("page_number", 1))
            docs[doc_id]["chunk_count"] += 1

        return [
            {
                "document_id": d["document_id"],
                "title": d["title"],
                "page_count": len(d["pages"]),
                "chunk_count": d["chunk_count"]
            }
            for d in docs.values()
        ]

# Global instance
vector_store = VectorStore()
