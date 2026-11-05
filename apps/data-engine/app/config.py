import os
from typing import List
from pydantic import BaseModel, Field

class Settings(BaseModel):
    APP_NAME: str = "SprintLens Data Engine"
    APP_VERSION: str = "1.0.0"
    HOST: str = Field(default_factory=lambda: os.getenv("DATA_ENGINE_HOST", "0.0.0.0"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("DATA_ENGINE_PORT", "8000")))
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

settings = Settings()