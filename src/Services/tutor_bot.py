from src.Models.tutor_bot import TutorSessionRequest, TutorSessionResponse
from src.LLMs.gemini_integration import GeminiClient
from Models.static_assessment import SubjectType
from typing import Optional

class TutorBotService:
    def __init__(self):
        self.tutor_bot = GeminiClient()
        self.response_schema = {
            "type": "object",
            "properties": {
                "explanation": {"type": "string"},
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "follow_up_question": {"type": "string"}
            },
            "required": ["explanation"]
        }

    async def generate_tutor_response(self, request: TutorSessionRequest) -> TutorSessionResponse:
        # Construct the prompt with full context
        prompt = self._construct_prompt(request)
        
        # Generate structured response from LLM
        response = await self.tutor_bot.generate_structured_data(
            prompt=prompt,
            response_schema=self.response_schema
        )
        
        # Create updated chat history
        updated_history = self._update_chat_history(request, response)
        
        return TutorSessionResponse(
            explanation=response['explanation'],
            updated_chat_history=updated_history
        )

    def _construct_prompt(self, request: TutorSessionRequest) -> str:
        """Build context-aware prompt for tutoring session"""
        return f"""
        Act as an expert tutor for {request.subject.subject.value}. The student is in class {request.student.student_class} 
        with {request.student.student_performance}% average performance. Learning style: {request.student.student_learning_style}, 
        preferred pace: {request.student.student_pace}.

        Current chapter: {request.subject.chapter}
        Topic: {request.subject.topic_description}

        Conversation history:
        {self._format_chat_history(request.chat_history)}

        New student message: {request.new_message}

        Provide:
        1. Clear explanation addressing the student's query
        2. 2-3 key points to reinforce understanding
        3. A thoughtful follow-up question to check comprehension
        """

    def _format_chat_history(self, history: list) -> str:
        return "\n".join(
            [f"{msg.sender}: {msg.content}" 
             for msg in history[-5:]]  # Keep last 5 messages for context
        )

    def _update_chat_history(self, request: TutorSessionRequest, response: dict) -> list:
        """Update chat history with new messages"""
        updated_history = request.chat_history.copy()
        
        # Add student message
        updated_history.append({
            "content": request.new_message,
            "sender": "student",
        })
        
        # Add tutor response
        updated_history.append({
            "content": response['explanation'],
            "sender": "tutor",
            "metadata": {
                "key_points": response.get('key_points', []),
                "follow_up_question": response.get('follow_up_question')
            }
        })
        
        return updated_history