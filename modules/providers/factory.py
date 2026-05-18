import os
from modules.config import get_provider_name, validate_env, get_env
from modules.providers.base import BaseProvider


def get_provider(provider_name: str | None = None) -> BaseProvider:
    name = (provider_name or get_provider_name()).strip().lower()
    if name == "groq":
        from modules.providers.groq import GroqProvider
        return GroqProvider()
    else:
        raise ValueError(f"Unknown provider: {name}. Use: groq")


def get_available_providers() -> list[tuple[str, str]]:
    providers = []

    # Groq cloud (free tier)
    providers.append(("groq", "☁️ Groq (Free Cloud)"))

    return providers

