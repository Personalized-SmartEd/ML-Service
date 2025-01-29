import os
import google.generativeai as genai
from json import JSONDecodeError
import json
import re
from typing import Dict, Any
import logging
import asyncio
from dotenv import load_dotenv

from src.Models.quiz import Quiz
load_dotenv('../.env')

logger = logging.getLogger(__name__)
GEMINI_API_KEY =   os.getenv('GEMINI_API_KEY')


class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key is required")
        genai.configure(api_key=GEMINI_API_KEY)
        self.text_model = genai.GenerativeModel('gemini-pro')
        self.embedding_model = 'models/embedding-001'

    def generate_quiz(self, prompt: str) -> Dict[str, Any]:
        """Generate structured quiz data with JSON validation"""
        try:
            full_prompt = f"""
            {prompt}
            Respond ONLY with valid JSON matching this schema:
            {Quiz.model_json_schema()}
            No additional text or formatting.
            """
            response = self.text_model.generate_content(
                full_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return self._validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Quiz generation failed: {str(e)}") from e

    def generate_recommendations(self, prompt: str) -> str:
        """Generate markdown-formatted recommendations"""
        try:
            response = self.text_model.generate_content(
                f"{prompt}\nFormat response using markdown lists and headings.",
                generation_config={"temperature": 0.3}
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Recommendation generation failed: {str(e)}") from e

    async def generate_embeddings(self, text: str) -> list[float]:
        """Async text embeddings using thread executor"""
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,  # Uses default executor
                lambda: genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
            )
            return result['embedding']
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {str(e)}") from e
        
    def _validate_json(self, text: str) -> Dict[str, Any]:
        """Clean and validate Gemini's JSON response"""
        try:
            # First try direct parse
            return json.loads(text)
        except JSONDecodeError:
            # Attempt to extract JSON from markdown
            cleaned = re.sub(r'^```json|```$', '', text, flags=re.MULTILINE)
            return json.loads(cleaned.strip())
        except Exception as e:
            raise ValueError(f"Invalid JSON response: {text}") from e
        
    async def generate_structured_data(self, prompt: str, response_schema: dict) -> dict:
            """Generic structured data generation with schema validation"""
            try:
                system_prompt = f"""
                {prompt}
                Respond ONLY with valid JSON strictly following this schema:
                {json.dumps(response_schema, indent=2)}
                
                Important:
                1. No markdown formatting
                2. No additional text
                3. Use double quotes
                4. Order fields as in schema
                """

                response = self.text_model.generate_content(
                    system_prompt,
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 5000
                    }
                )
                
                return self._validate_json(response.text)
            except Exception as e:
                raise RuntimeError(f"Structured data generation failed: {str(e)}") from e

    def _validate_json(self, text: str) -> dict:
        """Robust JSON cleaning and validation"""
        try:
            # First try direct parse
            return json.loads(text)
        except JSONDecodeError:
            # Handle common Gemini response patterns
            cleaned = re.sub(
                r'^[^{[]*|[^}\]]*$',  # Remove non-JSON prefix/suffix
                '', 
                text, 
                flags=re.DOTALL
            )
            return json.loads(cleaned.strip())
        except Exception as e:
            raise ValueError(f"Invalid JSON response: {text[:200]}...") from e
        
    @staticmethod
    def clean_response(text: str) -> str:
        """Remove markdown formatting and extra spaces"""
        # Remove markdown headers, bold, italics
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\*\*|\*|__|_', '', text)
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Collapse multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
        
    async def generate_learning_style_explanation(self, learning_style: str) -> str:
        """Generate learning style explanation with study tips"""
       
        prompt = f"""
        Generate a concise explanation of the {learning_style} learning style using this exact format:

        [1-sentence definition]. Key characteristics:
        - Characteristic 1
        - Characteristic 2 
        - Characteristic 3

        Study strategies:
        * Strategy 1 (Implementation tip)
        * Strategy 2 (Implementation tip) 
        * Strategy 3 (Implementation tip)

        Technology tools: Comma-separated list
        Common pitfall: [one key point]

        Requirements:
        1. Use ONLY plain text with dashes and asterisks
        2. No markdown, headers
        3. Keep sentences short (<15 words)
        4. Focus on actionable advice
        5. School subject examples in parentheses
        6. Max 500 characters per section
        7. Use Emojis for emphasis (optional)

        Example for visual learning:
        Learns best through images and spatial understanding. Key characteristics:
        - Prefers diagrams over text
        - Remembers faces better than names
        - Uses color-coding effectively

        Study strategies:
        * Create mind maps (history timelines)
        * Watch video demonstrations (science experiments)
        * Use flashcards with pictures (vocabulary)

        Technology tools: Canva, YouTube, Quizlet
        Common pitfall: Overlooking textual details
        """
        try:
            response = await self.generate_structured_data(
                prompt=prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "maxLength": 500
                        }
                    },
                    "required": ["description"]
                }
            )
            return self.clean_response(response["description"])
        
        except Exception as error:
            logger.error(f"Explanation generation failed: {error}")
            return f"Customized {learning_style} learning approach description"
    
    