from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
	env: str = Field(default="development", alias="ENV")
	port: int = Field(default=8000, alias="PORT")
	gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
	chat_model: str = Field(default="models/gemini-2.5-flash", alias="CHAT_MODEL")
	embedding_model: str = Field(default="intfloat/e5-base-v2", alias="EMBEDDING_MODEL")
	pinecone_api_key: str = Field(default="", alias="PINECONE_API_KEY")
	pinecone_index: str = Field(default="ai-customer-bot-faq", alias="PINECONE_INDEX")
	db_url: str = Field(default="sqlite+aiosqlite:///./data/app.db", alias="DB_URL")
	log_level: str = Field(default="INFO", alias="LOG_LEVEL")

	# RAG parameters
	top_k: int = Field(default=3, alias="TOP_K")
	score_threshold: float = Field(default=0.75, alias="SCORE_THRESHOLD")
	max_context_chars: int = Field(default=1200, alias="MAX_CONTEXT_CHARS")

	class Config:
		env_file = ".env"

settings = Settings()
