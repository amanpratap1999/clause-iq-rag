import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PORT: int = int(os.getenv("PORT", "8001"))
    HOST: str = os.getenv("HOST", "127.0.0.1")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # Qdrant
    QDRANT_STORAGE_PATH: str = os.getenv("QDRANT_STORAGE_PATH", "./qdrant_storage")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "policy_documents")

    # LLM
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "").strip()
    MOCK_LLM: bool = os.getenv("MOCK_LLM", "true").lower() in ("true", "1", "yes") or not LLM_API_KEY
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    # Embedding
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local").lower()

settings = Settings()
