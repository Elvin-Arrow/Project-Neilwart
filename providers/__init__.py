from .base import LLMProvider
from .ollama_provider import OllamaProvider

def get_provider(provider_name: str) -> LLMProvider:
    provider_name = provider_name.lower().strip()
    
    if provider_name == "ollama":
        return OllamaProvider()
    elif provider_name == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "gemini":
        from .gemini_provider import GeminiProvider
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown provider '{provider_name}'. Supported providers: ollama, openai, gemini")
