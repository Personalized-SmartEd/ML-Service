from typing import List, Optional
from src.LLMs.gemini_integration import GeminiClient
from src.Models.doubt_bot import DoubtBotRequest, DoubtBotResponse
from src.Models.static_assessment import SubjectType

class DoubtBotService:
    def __init__(self):
        self.gemini = GeminiClient()
        
    def _construct_prompt(self, request: DoubtBotRequest) -> str:
        """Constructs a context-aware prompt for the AI model"""
        prompt = f"""As a knowledgeable tutor, help solve this {request.subject.value} doubt.
        
Student Grade Level: {request.student.student_class}
Subject: {request.subject.value}
Question: {request.doubt.question}

Please provide:
1. A clear, detailed explanation
2. 2-3 relevant follow-up questions to check understanding
"""
        if request.doubt.image_description:
            prompt += f"\nContext from image: {request.doubt.image_description}"
            
        return prompt

    async def solve_doubt(self, request: DoubtBotRequest) -> DoubtBotResponse:
        """Process student doubt with Gemini AI"""
        try:
            # Construct the base prompt
            prompt = self._construct_prompt(request)
            
            # 1. Handle image-based doubt
            if request.doubt.image_url:
                response = await self.gemini.generate_with_image(
                    prompt=prompt,
                    image_url=request.doubt.image_url
                )
            else:
            # 2. Text-only doubt
                response = await self.gemini.generate_structured_data(prompt=prompt, 
                        response_schema={
                            "type":"object",
                            "properties": {
                                "explanation" : {"type" : "string"},
                                "follow_up_questions" : {
                                    "type" : "array",
                                    "minItems": 3,
                                    "maxItems": 3,
                                    "items" : {"type" : "string"},
                                }
                            }
                        }
                    )
                return DoubtBotResponse(explanation=response['properties']['explanation'], follow_up_questions=response['properties']['follow_up_questions'])
            
        except Exception as e:
            print(f"Error processing doubt: {str(e)}")
            return DoubtBotResponse(
                explanation="I apologize, but I encountered an error while processing your doubt. "
                          "Please try rephrasing your question or contact support if the issue persists.",
                follow_up_questions=["Could you please rephrase your question?"]
            )
    
    def _parse_gemini_response(self, response: str) -> tuple[str, List[str]]:
        """Parse Gemini response to extract explanation and follow-up questions"""
        try:
            # Split response into explanation and questions
            # This implementation might need adjustment based on actual Gemini response format
            parts = response.split("Follow-up Questions:")
            
            explanation = parts[0].strip()
            questions = []
            
            if len(parts) > 1:
                # Extract questions, assuming they're numbered or bulleted
                question_text = parts[1].strip()
                # Simple parsing - adjust based on actual format
                questions = [q.strip().lstrip('123.•- ') 
                           for q in question_text.split('\n') 
                           if q.strip()]
                
            return explanation, questions[:3]  # Limit to 3 questions
            
        except Exception as e:
            # If parsing fails, return the full response as explanation
            return response.strip(), []