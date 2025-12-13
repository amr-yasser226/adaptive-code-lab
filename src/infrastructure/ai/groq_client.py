import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Check if groq package is available
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:     
    GROQ_AVAILABLE = False
    Groq = None


class GroqClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model name (defaults to GROQ_MODEL env var)
        """
        if not GROQ_AVAILABLE:
            raise ImportError("groq package not installed. Run: pip install groq")
        
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided and not found in environment")
        
        self.client = Groq(api_key=self.api_key)
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")
    
    def generate_hint(self, code: str, error_message: Optional[str] = None, context: Optional[str] = None) -> str:

        system_prompt = """You are a helpful coding tutor. Provide a helpful hint without giving away the full solution.
Be encouraging and guide the student toward understanding, not just fixing."""
        
        user_content = f"Code:\n```\n{code}\n```"
        if error_message:
            user_content += f"\n\nError: {error_message}"
        if context:
            user_content += f"\n\nContext: {context}"
        user_content += "\n\nProvide a helpful hint."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        return self.chat(messages, temperature=0.7)
    
    def review_code(self, code: str, assignment_description: Optional[str] = None) -> str:
        system_prompt = """You are a code reviewer. Provide constructive feedback on:
1. Code quality and style
2. Potential bugs or issues
3. Suggestions for improvement
Be specific and educational."""
        
        user_content = f"Review this code:\n```\n{code}\n```"
        if assignment_description:
            user_content += f"\n\nAssignment: {assignment_description}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        return self.chat(messages, temperature=0.3)
    
    def get_model_name(self) -> str:
        return self.model
