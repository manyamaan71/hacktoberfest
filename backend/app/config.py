import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GEMMA_PROVIDER: str = os.getenv("GEMMA_PROVIDER", "google")
    GEMMA_API_KEY: Optional[str] = os.getenv("GEMMA_API_KEY")
    GEMMA_MODEL: str = os.getenv("GEMMA_MODEL", "gemma-4b")
    GEMMA_API_BASE_URL: Optional[str] = os.getenv("GEMMA_API_BASE_URL")
    MAX_AGENT_STEPS: int = int(os.getenv("MAX_AGENT_STEPS", "6"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    MAX_REPOSITORY_FILES: int = int(os.getenv("MAX_REPOSITORY_FILES", "1500"))
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", "524288"))
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

settings = Settings()
