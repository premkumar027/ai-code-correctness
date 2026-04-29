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

class BaseModel(ABC):

    def __init__(self, model_name: str):
        self.model_name = model_name
    @abstractmethod
    def generate(self, prompt:str) -> ModelResponse:
        pass
