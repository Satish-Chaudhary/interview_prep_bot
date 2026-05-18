import json
import time
from typing import Any, Optional

from openai import OpenAI

from modules.config import get_env, get_timeout
from modules.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.api_key = get_env("OPENAI_API_KEY")
        self.model = get_env("OPENAI_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(api_key=self.api_key)
        self.timeout = get_timeout()

    def generate_text(self, prompt: str, **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
                timeout=self.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def generate_json(self, prompt: str, schema: Optional[dict] = None, **kwargs) -> Optional[dict[str, Any]]:
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
                raise RuntimeError(f"OpenAI error after retries: {e}") from e
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
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
