from time import time
from langchain_google_genai import ChatGoogleGenerativeAI
from src.models.base import BaseModel, ModelResponse, extract_usage

class GoogleModel(BaseModel):

    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name)
        self.llm = ChatGoogleGenerativeAI(
            model= model_name,
            google_api_key= api_key
        )

    def generate(self, prompt:str):
        try:
            start = time()
            result = self.llm.invoke(prompt)
            elapsed = time() - start
            in_tok, out_tok = extract_usage(result)

            return ModelResponse(
                model_name= self.model_name,
                prompt= prompt,
                response = result.content,
                response_time = elapsed,
                input_tokens=in_tok,
                output_tokens=out_tok,
            )
        except Exception as e:

            return ModelResponse(
                model_name= self.model_name,
                prompt= prompt,
                response="",
                response_time=0.0,
                error=str(e)
            )