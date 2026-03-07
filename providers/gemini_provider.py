import os
import time
from google import genai
from .base import LLMProvider
from config.loader import config
from PIL import Image
import io

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.model_name = config['model']['gemini']['name']
        self.max_retries = config['model']['gemini']['max_retries']
        self.base_delay = config['model']['gemini']['base_delay']
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
    def generate(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                return response.text or ""
            except Exception as e:
                wait_time = self.base_delay * (2 ** attempt)
                print(f"  [Error] calling Gemini API: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{self.max_retries})")
                time.sleep(wait_time)
        return ""

    def generate_with_image(self, prompt: str, image_bytes: bytes) -> str:
        img = Image.open(io.BytesIO(image_bytes))
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, img]
                )
                return response.text or ""
            except Exception as e:
                wait_time = self.base_delay * (2 ** attempt)
                print(f"  [Error] calling Gemini API with image: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{self.max_retries})")
                time.sleep(wait_time)
        return ""
