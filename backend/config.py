from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # LLM
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    llm_provider: str = Field(default="groq", env="LLM_PROVIDER")
    llm_model: str = Field(default="llama-3.1-8b-instant", env="LLM_MODEL")

    # Search
    tavily_api_key: str = Field(default="", env="TAVILY_API_KEY")

    # App
    database_url: str = Field(
        default="sqlite+aiosqlite:///./devils_advocate.db",
        env="DATABASE_URL"
    )
    cors_origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")
    mcp_config_path: str = Field(default="../mcp_config.json", env="MCP_CONFIG_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
