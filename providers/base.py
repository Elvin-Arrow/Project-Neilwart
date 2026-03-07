from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers used in the application.
    """
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Send a text prompt to the LLM and return the generated text response.
        """
        pass
        
    @abstractmethod
    def generate_with_image(self, prompt: str, image_bytes: bytes) -> str:
        """
        Send a text prompt along with an image to the LLM.
        """
        pass
        
