from app.core.config import settings
from app.services.ai.base import LLMProvider
from app.services.ai.claude import ClaudeLLMProvider
from app.services.ai.mock import MockLLMProvider
from app.services.ai.ollama import OllamaLLMProvider


class AIProviderConfigurationError(RuntimeError):
    """Raised when the configured AI provider cannot be constructed."""


def get_llm_provider(provider_override: str | None = None) -> LLMProvider:
    """Resolve a provider, with optional local-only override per workspace policy."""
    provider = (provider_override or settings.ai_provider).strip().lower()

    if provider == "mock":
        return MockLLMProvider()

    if provider == "claude":
        if not settings.anthropic_api_key:
            raise AIProviderConfigurationError(
                "Claude provider is selected but the provider key is not configured."
            )
        return ClaudeLLMProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        )

    if provider == "ollama":
        return OllamaLLMProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )

    raise AIProviderConfigurationError(
        "Unsupported AI provider. Expected one of: mock, claude, ollama."
    )
