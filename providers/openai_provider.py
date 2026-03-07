import os
import time
from openai import OpenAI
import base64
from .base import LLMProvider
from config.loader import config

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.model_name = config['model']['openai']['name']
        self.max_retries = config['model']['openai']['max_retries']
        self.base_delay = config['model']['openai']['base_delay']
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def generate(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                wait_time = self.base_delay * (2 ** attempt)
                print(f"  [Error] calling OpenAI API: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{self.max_retries})")
                time.sleep(wait_time)
        return ""

    def generate_with_image(self, prompt: str, image_bytes: bytes) -> str:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                wait_time = self.base_delay * (2 ** attempt)
                print(f"  [Error] calling OpenAI API with image: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{self.max_retries})")
                time.sleep(wait_time)
        return ""
