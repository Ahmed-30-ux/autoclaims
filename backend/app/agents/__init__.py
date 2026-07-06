import json
from app.config import settings
from app.services.qwen_client import chat_json
from app.db import get_policy, update_claim


class BaseAgent:
    name: str = "base"
    model: str = settings.qwen_model_flash

    def __init__(self):
        self.system_prompt = ""

    def build_messages(self, context: dict) -> list[dict]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": json.dumps(context, indent=2, default=str)},
        ]

    async def run(self, context: dict) -> dict:
        messages = self.build_messages(context)
        result = chat_json(self.model, messages, temperature=0.2)
        return result
