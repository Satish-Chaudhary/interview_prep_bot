import os
from typing import Optional

from modules.config import (
    get_assistant_max_tokens,
    get_assistant_temperature,
)
from modules.providers.factory import get_provider

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")


def _read_prompt(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class AssistantBot:
    def __init__(self):
        self.provider = get_provider()
        self.temperature = get_assistant_temperature()
        self.max_tokens = get_assistant_max_tokens()

    def is_available(self) -> tuple[bool, str]:
        # Groq API doesn't need a local connection check like Ollama did
        # We can just return True and any HTTP errors will be caught during generate
        return True, ""

    def get_response(
        self,
        user_message: str,
        current_question: Optional[str] = None,
        context_enabled: bool = False,
        stage: Optional[str] = None,
    ) -> str:
        system = _read_prompt("assistant_system.txt")

        context = ""
        if context_enabled and current_question:
            context = f"\nThe user is currently on this interview question:\n{current_question}\n"
            
        if stage == "interview":
            context += "\n[CRITICAL RULE]: The user is CURRENTLY TAKING THE INTERVIEW. DO NOT give them the direct answer, DO NOT write code for them, and DO NOT solve the problem. Only act as an interviewer giving a small nudge or hint to point them in the right direction.\n"

        if context_enabled and current_question:
            full_prompt = f"{system}\n{context}\n\nUser question: {user_message}\n\nAssistant:"
        else:
            full_prompt = f"{system}\n{context}\nUser question: {user_message}\n\nAssistant:"

        try:
            return self.provider.generate_text(
                full_prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            return f"I'm having trouble connecting. Error: {e}"
