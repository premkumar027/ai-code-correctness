from src.config import MODEL_CONFIGS
from src.models.openai_model import OpenAIModel
from src.models.anthropic_model import AnthropicModel
from src.models.google_model import GoogleModel

def get_model(name: str):
    """Give it a model name from config, get back the right wrapper.
    Usage:
        model = get_model("gpt-5.5")
        result = model.generate("Write Dijkstra")
    """
    config = MODEL_CONFIGS[name]
    provider = config['provider']

    if provider == 'openai':
        return OpenAIModel(config['model_name'], config['api_key'])
    
    elif provider == 'openai_compatible':
        return OpenAIModel(config['model_name'], config['api_key'], config['base_url'])
    
    elif provider == 'anthropic':
        return AnthropicModel(config['model_name'], config['api_key'])
    
    elif provider == 'google':
        return GoogleModel(config['model_name'], config['api_key'])