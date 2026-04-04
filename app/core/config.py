from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SCM AI Troubleshooter"
    environment: str = "dev"
    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    
    embedding_model: str = "text-embedding-3-small"
    chroma_collection_name: str = "manual_chunks"
    chroma_persist_directory: str = "chroma_db"
    uploads_directory: str = "app/uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()