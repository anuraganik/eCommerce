import httpx

from app.services.ai.base import LLMMessage, LLMProvider


class OllamaProviderError(RuntimeError):
    pass


class OllamaLLMProvider(LLMProvider):
    """Local-inference provider for privacy-sensitive workspaces."""

    def __init__(self, base_url: str, model: str, timeout_seconds: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate_response(self, messages: list[LLMMessage]) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": message.role, "content": message.content} for message in messages
            ],
            "stream": False,
        }
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat", json=payload, timeout=self.timeout_seconds
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaProviderError(
                f"Local Ollama provider at {self.base_url} is unreachable or errored: {exc}"
            ) from exc

        data = response.json()
        content = (data.get("message") or {}).get("content")
        if not content:
            raise OllamaProviderError("Ollama response contained no message content.")
        return str(content).strip()
