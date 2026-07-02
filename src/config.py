import os
from dotenv import load_dotenv

load_dotenv()

MODEL_CONFIGS = {
    'gpt-5.5':{
        'provider':'openai', 
        'model_name':'gpt-5.5', 
        'api_key':os.getenv("OPENAI_API_KEY")
        },

    'gpt-5.4-mini':{
        'provider':'openai', 
        'model_name':'gpt-5.4-mini', 
        'api_key':os.getenv("OPENAI_API_KEY")
        },

    'claude-opus-4-7':{
        'provider':'anthropic', 
        'model_name':'claude-opus-4-7', 
        'api_key':os.getenv('ANTHROPIC_API_KEY')
        },

    'claude-sonnet-4-6':{
        'provider':'anthropic', 
        'model_name':'claude-sonnet-4-6', 
        'api_key':os.getenv("ANTHROPIC_API_KEY")
        },

    'gemini-2.5-flash':{
        'provider':'google',
        'model_name':'gemini-2.5-flash',
        'api_key':os.getenv("GOOGLE_AI_API_KEY")
        },

    'gemini-3.5-flash': {
        'provider': 'google',
        'model_name': 'gemini-3.5-flash',
        'api_key': os.getenv("GOOGLE_AI_API_KEY")
        },

    'gemma-4-27b':{
        'provider':'google',
        'model_name':'gemma-4-27b-it',
        'api_key': os.getenv("GOOGLE_AI_API_KEY")
        },

    'deepseek-v4-pro':{
        'provider':'openai_compatible', 
        'model_name':'deepseek-v4-pro', 
        'api_key':os.getenv("DEEPSEEK_API_KEY"), 
        'base_url': 'https://api.deepseek.com'
        }
}

def get_model_names() -> list[str]:
    return list(MODEL_CONFIGS.keys())


# Price in USD per 1,000,000 tokens, as (input, output), keyed by the model
# config name above. Anthropic values are current list prices. The others are
# PLACEHOLDERS — replace them with the real per-model pricing so cost logging is
# accurate. A model missing here logs tokens but a NULL cost (never crashes).
PRICING = {
    'gpt-5.5':           (1.25, 10.0),   # PLACEHOLDER — update
    'gpt-5.4-mini':      (0.25,  2.0),   # PLACEHOLDER — update
    'claude-opus-4-7':   (5.0,  25.0),
    'claude-sonnet-4-6': (3.0,  15.0),
    'gemini-2.5-flash':  (0.30,  2.5),   # PLACEHOLDER — update
    'gemini-3.5-flash':  (0.30,  2.5),   # PLACEHOLDER — update
    'gemma-4-27b':       (0.0,   0.0),   # PLACEHOLDER — often free tier
    'deepseek-v4-pro':   (0.28,  0.42),  # PLACEHOLDER — update
}


def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float | None:
    """USD cost of a single call, or None if the model's pricing is unknown."""
    price = PRICING.get(model_name)
    if not price:
        return None
    price_in, price_out = price
    return (input_tokens / 1_000_000) * price_in + (output_tokens / 1_000_000) * price_out