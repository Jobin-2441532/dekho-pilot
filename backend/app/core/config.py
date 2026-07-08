import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    _db_url = os.getenv("DATABASE_URL", "sqlite:///./dekho.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    elif _db_url.startswith("sqlite:///"):
        db_file = _db_url.replace("sqlite:///", "", 1)
        if not os.path.isabs(db_file):
            backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            db_file = os.path.abspath(os.path.join(backend_root, db_file))
        _db_url = f"sqlite:///{db_file}"
    DATABASE_URL: str = _db_url
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    DATA_DIR: str = os.getenv("DATA_DIR", "../data")
    KNOWLEDGE_BASE_DIR: str = os.getenv("KNOWLEDGE_BASE_DIR", "../knowledge-base")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
