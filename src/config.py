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