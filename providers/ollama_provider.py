import ollama
import time
from .base import LLMProvider
from config.loader import config

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.model_name = config['model']['ollama']['name']
        self.max_retries = config['model']['ollama']['max_retries']
        self.base_delay = config['model']['ollama']['base_delay']
        
        self._check_ollama_and_model()
        
    def _check_ollama_and_model(self):
        """
        Checks if the Ollama service is running and if the requested model is available.
        """
        print(f"Checking for Ollama service and model '{self.model_name}'...")
        try:
            response = ollama.list()
            
            if hasattr(response, 'models'):
                available_models = [m.model for m in response.models]
            else:
                available_models = [m.get('model', m.get('name', '')) for m in response.get('models', [])]
                
            model_found = any('gemma' in m or m.startswith(self.model_name) for m in available_models)
            
            if not model_found:
                print(f"Error: Model '{self.model_name}' not found in Ollama.")
                print(f"Please run 'ollama run {self.model_name}' to download it.")
                import sys
                sys.exit(1)
                
            print(f"Success: Connected to Ollama and found '{self.model_name}'.")
        except Exception as e:
            print("Error: Could not connect to Ollama.")
            print("Please ensure the Ollama application is running (http://localhost:11434).")
            print(f"Details: {e}")
            import sys
            sys.exit(1)
        
    def generate(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                response = ollama.generate(
                    model=self.model_name,
                    prompt=prompt
                )
                return response.get('response', '')
            except Exception as e:
                wait_time = self.base_delay * (2 ** attempt)
                print(f"  [Error] calling Ollama API: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{self.max_retries})")
                time.sleep(wait_time)
        return ""

    def generate_with_image(self, prompt: str, image_bytes: bytes) -> str:
        for attempt in range(self.max_retries):
            try:
                response = ollama.generate(
                    model=self.model_name,
                    prompt=prompt,
                    images=[image_bytes]
                )
                return response.get('response', '')
            except Exception as e:
                wait_time = self.base_delay * (2 ** attempt)
                print(f"  [Error] calling Ollama API with image: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{self.max_retries})")
                time.sleep(wait_time)
        return ""
