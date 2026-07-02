from dataclasses import dataclass
from time import time
from abc import ABC, abstractmethod

@dataclass
class ModelResponse:

    model_name: str
    prompt: str
    response: str
    response_time: float
    error: str | None = None  # None means success
    input_tokens: int = 0
    output_tokens: int = 0


def extract_usage(result) -> tuple[int, int]:
    """Pull (input_tokens, output_tokens) from a LangChain result's usage_metadata.

    All the chat models we use (Anthropic, OpenAI, Google, DeepSeek) populate
    `usage_metadata`. Returns (0, 0) when it is missing so callers never crash.
    """
    usage = getattr(result, "usage_metadata", None) or {}
    return usage.get("input_tokens", 0) or 0, usage.get("output_tokens", 0) or 0


class BaseModel(ABC):

    def __init__(self, model_name: str):
        self.model_name = model_name
    @abstractmethod
    def generate(self, prompt:str) -> ModelResponse:
        pass
