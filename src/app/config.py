from pydantic import BaseModel
import os


class Settings(BaseModel):
    use_ollama: bool = os.getenv("USE_OLLAMA", "true").lower() == "true"
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1:8b")
    ollama_embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")


    # openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # openai_base_url: str | None = os.getenv("OPENAI_BASE_URL")
    # openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


    chroma_dir: str = os.getenv("CHROMA_DIR", ".chroma")
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "food_kb")


    otlp_endpoint: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    service_name: str = os.getenv("OTEL_SERVICE_NAME", "food-rating-agent")
    environment: str = os.getenv("OTEL_ENVIRONMENT", "dev")


    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    hitl_secret: str = os.getenv("HITL_SECRET", "change-me")


    tesseract_cmd: str | None = os.getenv("TESSERACT_CMD") 


settings = Settings()