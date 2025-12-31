import os
from dataclasses import dataclass


DEFAULT_OLLAMA_URL = "http://host.docker.internal:11434"
DEFAULT_OLLAMA_MODEL = "html-model:latest"


@dataclass(frozen=True)
class Settings:
    ollama_url: str
    ollama_model: str


def get_settings() -> Settings:
    """
    Minimal config helper.

    Environment variables:
    - OLLAMA_URL (default: http://host.docker.internal:11434)
    - OLLAMA_MODEL (default: html-model:latest)
    """
    ollama_url = os.getenv("OLLAMA_URL", DEFAULT_OLLAMA_URL).rstrip("/")
    ollama_model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    return Settings(ollama_url=ollama_url, ollama_model=ollama_model)


