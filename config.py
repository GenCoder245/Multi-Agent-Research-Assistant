#from functools import lru_cache
import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore",case_sensitive=False,)

    # App metadata
    app_name: str = "Multi-Agent Technical Research Assistant"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # Required secrets
    openai_api_key: SecretStr | None = None
    gemini_api_key: SecretStr
    tavily_api_key: SecretStr

    # Model config
    openai_chat_model: str = "gpt-5-nano-2025-08-07"
    gemini_chat_model: str = "gemini-3.5-flash-lite"

    llm_temperature : float = Field(default= 0.5, ge= 0.0, le = 1.0)
    max_llm_retries : int = Field(default=3, ge=0, le=5)

    # Langsmith Tracing related:
    langsmith_tracing: str = Field(default="false")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com")
    langsmith_api_key : SecretStr | None = None
    langsmith_project: str = Field(default="demo_project")

    sqlite_database_name : str = "checkpoints.sqlite"


    @property
    def openai_api_key_value(self) -> str:
        if self.openai_api_key:
            return self.openai_api_key.get_secret_value()
        else:
            return ""

    @property
    def gemini_api_key_value(self) -> str:
        return self.gemini_api_key.get_secret_value()

    @property
    def tavily_api_key_value(self) -> str:
        return self.tavily_api_key.get_secret_value()
    

# @lru_cache
def get_settings() -> Settings:

    settings = Settings()
    # Sync values to os.environ so LangSmith SDK can read them
    os.environ["LANGSMITH_TRACING"] = settings.langsmith_tracing
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project

    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key.get_secret_value() 

    os.environ["TAVILY_API_KEY"] = settings.tavily_api_key_value

    return settings 
