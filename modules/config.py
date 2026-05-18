import os
from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def get_provider_name() -> str:
    # CORE_PROVIDER takes precedence; fall back to LLM_PROVIDER for compatibility
    return get_env("CORE_PROVIDER", get_env("LLM_PROVIDER", "groq")).strip().lower()


def _is_placeholder(value: str) -> bool:
    placeholders = [
        "sk-your-deepseek-key-here",
        "gsk_your-groq-key-here",
        "sk-your-openai-key-here",
        "your-api-key",
        "your-groq-api-key-here",
        "",
    ]
    return value.strip() in placeholders


def validate_env() -> list[str]:
    warnings = []
    provider = get_provider_name()

    # Only warn about paid-API keys when the matching provider is selected
    if provider == "deepseek":
        ds_key = get_env("DEEPSEEK_API_KEY")
        if _is_placeholder(ds_key):
            warnings.append("DEEPSEEK_API_KEY is missing or still a placeholder. Set it in .env")

    if provider == "groq":
        groq_key = get_env("GROQ_API_KEY")
        if _is_placeholder(groq_key):
            warnings.append("GROQ_API_KEY is missing or still a placeholder. Set it in .env")

    if provider == "openai":
        openai_key = get_env("OPENAI_API_KEY")
        if _is_placeholder(openai_key):
            warnings.append("OPENAI_API_KEY is missing or still a placeholder. Set it in .env")

    return warnings


def get_deepseek_config() -> dict:
    return {
        "api_key": get_env("DEEPSEEK_API_KEY"),
        "model": get_env("DEEPSEEK_MODEL", "deepseek-chat"),
    }


def get_groq_config() -> dict:
    return {
        "api_key": get_env("GROQ_API_KEY"),
        # llama-3.1-8b-instant = fast, free, great for JSON tasks
        "model": get_env("GROQ_MODEL", "llama-3.1-8b-instant"),
    }


def get_active_model_name(provider: str) -> str:
    if provider == "groq":
        return get_groq_config().get("model", "Unknown")
    return "Unknown"




def get_core_temperature() -> float:
    try:
        return float(get_env("CORE_TEMPERATURE", "0.3"))
    except ValueError:
        return 0.3


def get_core_max_tokens() -> int:
    try:
        return int(get_env("CORE_MAX_TOKENS", "1200"))
    except ValueError:
        return 1200


def get_assistant_temperature() -> float:
    try:
        return float(get_env("ASSISTANT_TEMPERATURE", "0.5"))
    except ValueError:
        return 0.5


def get_assistant_max_tokens() -> int:
    try:
        return int(get_env("ASSISTANT_MAX_TOKENS", "600"))
    except ValueError:
        return 600


def get_question_count() -> int:
    try:
        return int(get_env("QUESTION_COUNT", "10"))
    except ValueError:
        return 10


def get_temperature_questions() -> float:
    try:
        return float(get_env("TEMPERATURE_QUESTIONS", "0.7"))
    except ValueError:
        return 0.7


def get_temperature_evaluation() -> float:
    try:
        return float(get_env("TEMPERATURE_EVALUATION", "0.2"))
    except ValueError:
        return 0.2


def get_timeout() -> int:
    try:
        return int(get_env("TIMEOUT", "60"))
    except ValueError:
        return 60
