from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

LLMRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class LLMMessage:
    role: LLMRole
    content: str


class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, messages: list[LLMMessage]) -> str:
        """Generate an assistant response from normalized conversation history."""
