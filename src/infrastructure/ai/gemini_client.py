import os
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class GeminiClient:
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not provided and not found in environment")
        
        genai.configure(api_key=self.api_key)
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            raise RuntimeError(f"Gemini embedding API error: {e}")
    
    def get_model_name(self) -> str:
        """Return the model name being used."""
        return self.model
