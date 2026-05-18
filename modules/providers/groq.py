import json
import time
import requests
from typing import Any, Optional

from modules.config import get_groq_config, get_timeout
from modules.providers.base import BaseProvider


class GroqProvider(BaseProvider):
    """
    Groq cloud inference provider.
    Uses the Groq REST API (OpenAI-compatible format).
    Free tier: https://console.groq.com
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        cfg = get_groq_config()
        self.api_key = cfg["api_key"]
        self.model = cfg.get("model", "llama3-8b-8192")
        self.timeout = get_timeout()

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Get a free key at https://console.groq.com and add it to your .env or Streamlit Secrets."
            )

    def generate_text(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 1200),
        }
        
        if "response_format" in kwargs:
            payload["response_format"] = kwargs["response_format"]
        try:
            resp = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            err_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                err_msg += f" | Details: {e.response.text}"
            
            if "getaddrinfo failed" in str(e) or "NameResolutionError" in str(e):
                raise RuntimeError("Network Error: Could not reach api.groq.com. Please check your internet connection or DNS settings.") from e
            raise RuntimeError(f"Groq API Error: {err_msg}") from e

    def generate_json(self, prompt: str, schema: Optional[dict] = None, **kwargs) -> Optional[dict[str, Any]]:
        kwargs.setdefault("temperature", 0.3)
        kwargs.setdefault("max_tokens", 1200)
        
        # Groq specifically recommends response_format for JSON outputs
        kwargs["response_format"] = {"type": "json_object"}

        for attempt in range(kwargs.get("max_retries", 3)):
            try:
                text = self.generate_text(prompt, **kwargs)
                parsed = self._extract_json(text)
                if parsed:
                    return parsed
            except Exception as e:
                if attempt < kwargs.get("max_retries", 3) - 1:
                    time.sleep(1)
                    continue
                raise RuntimeError(f"Groq error after {attempt + 1} retries: {e}") from e
        return None

    @staticmethod
    def _extract_json(text: str) -> Optional[dict[str, Any]]:
        if "```" in text:
            lines = text.splitlines()
            cleaned = []
            inside = False
            for line in lines:
                s = line.strip()
                if s.startswith("```"):
                    inside = not inside
                    continue
                if not inside:
                    cleaned.append(line)
            text = "\n".join(cleaned)
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            return json.loads(text[start: end + 1])
        except json.JSONDecodeError:
            return None
