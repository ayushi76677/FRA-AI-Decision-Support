"""Runtime configuration. Demo is deliberately the safe default."""
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    database_mode: str = os.getenv("DATABASE_MODE", "demo").lower()
    database_url: str = os.getenv("DATABASE_URL", "")
    app_env: str = os.getenv("APP_ENV", "development")
    cors_origins: tuple[str, ...] = tuple(x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip())

    def __post_init__(self) -> None:
        if self.database_mode not in {"demo", "postgres"}:
            raise ValueError("DATABASE_MODE must be 'demo' or 'postgres'")

settings = Settings()
