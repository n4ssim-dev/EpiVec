from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "epigraph"
    postgres_user: str = "epigraph"
    postgres_password: str = "changeme"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # LLM
    anthropic_api_key: str = ""
    llm_provider: str = "claude"  # claude | ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # App
    environment: str = "development"
    log_level: str = "INFO"


settings = Settings()
