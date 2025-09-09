import json
from typing import Dict, Any, Optional

import requests

from .schema import ModelResponse, empty_response


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "mistral",
        timeout_seconds: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(self, system: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "format": "json",
            "stream": False,
        }
        if options:
            payload["options"] = options
        response = requests.post(url, json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()
        # Ollama chat returns { message: { role, content }, ... }
        return data.get("message", {}).get("content", "")


# Revert to simple parsing only


def parse_model_json(text: str) -> ModelResponse:
    try:
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            return empty_response()
        if "dishes" not in parsed or not isinstance(parsed.get("dishes"), list):
            parsed["dishes"] = []
        return parsed  # type: ignore[return-value]
    except json.JSONDecodeError:
        return empty_response()


def call_recipes(
    client: OllamaClient,
    system_prompt: str,
    user_prompt: str,
    retry_once_on_malformed: bool = True,
) -> ModelResponse:
    text = client.generate(system_prompt, user_prompt)
    parsed = parse_model_json(text)
    if parsed.get("dishes"):
        return parsed
    if retry_once_on_malformed:
        # Try again with a stronger reminder
        retry_prompt = user_prompt + "\nReturn only valid JSON per schema. No commentary."
        text = client.generate(system_prompt, retry_prompt)
        parsed = parse_model_json(text)
    return parsed


