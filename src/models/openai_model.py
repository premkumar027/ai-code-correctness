from time import time
from langchain_openai import ChatOpenAI
from src.models.base import BaseModel, ModelResponse, extract_usage

class OpenAIModel(BaseModel):
    """Wrapper for OpenAI and OpenAI-compatible APIs (GPT, DeepSeek)."""

    def __init__(self, model_name: str, api_key: str, base_url: str | None = None):
        super().__init__(model_name)

        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
        )

    def generate(self, prompt: str) -> ModelResponse:

        try:
            start = time()
            result = self.llm.invoke(prompt)
            elapsed = time() - start
            in_tok, out_tok = extract_usage(result)

            return ModelResponse(
                model_name= self.model_name,
                prompt = prompt,
                response = result.content,
                response_time= elapsed,
                input_tokens=in_tok,
                output_tokens=out_tok,
            )
        except Exception as e:
            return ModelResponse(
                model_name= self.model_name,
                prompt = prompt,
                response = "",
                response_time=0.0,
                error=str(e)
            )
