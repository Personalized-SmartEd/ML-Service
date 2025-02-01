import os
from dotenv import load_dotenv
load_dotenv('../.env')

class GroqConfiguration:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "deepseek-r1-distill-llama-70b")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
