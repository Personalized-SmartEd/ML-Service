import chromadb
from fastapi import HTTPException
from src.Models.tutor_bot import TutorSessionRequest, TutorSessionResponse
from src.LLMs.gemini_integration import GeminiClient
from src.Models.static_assessment import SubjectType
from typing import Optional
import os

CHROMA_DB_PATH = './tmp/data'

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
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.docs = ''
        

    async def generate_tutor_response(self, request: TutorSessionRequest) -> TutorSessionResponse:
        # extract relevant docs from the vector db
        self.load_docs(student_class=request.student.student_class, student_subject=request.subject.subject.value, query=request.new_message)

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
        # print('Docs before generating prompt : ',self.docs)
        """Build context-aware prompt for tutoring session"""
        return f"""
        Act as an expert tutor for {request.subject.subject.value}. The student is in class {request.student.student_class} 
        with {request.student.student_performance_from_1_to_100}% average performance. Learning style: {request.student.student_learning_style}, 
        preferred pace: {request.student.student_performance_level}.

        Current chapter: {request.subject.chapter}
        Topic: {request.subject.topic_description}

        Conversation history:
        {self._format_chat_history(request.chat_history)}
        Context: {self.docs}

        New student message: {request.new_message}

        Provide:
        1. Clear explanation addressing the student's query
        2. 2-3 key points to reinforce understanding
        3. A thoughtful follow-up question to check comprehension

        MUST FOLLOW: Try to generate a response related to the following context.
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
            "sender": "tutor-bot",
            "metadata": {
                "key_points": response.get('key_points', []),
                "follow_up_question": response.get('follow_up_question')
            }
        })
        
        return updated_history

    def get_available_classes_subjects(self):
        return self.chroma_client.list_collections()

    def load_docs(self, student_class:int, student_subject:str, query: str):
        if student_class  < 6 or 8 < student_class:
            raise HTTPException(status_code=303, detail='Can only handle class between 6 to 8')
        # print('DEBUG : ',os.listdir(path=CHROMA_DB_PATH), self.chroma_client.list_collections())
        book_name = 'Class-'+str(student_class) + '_'+student_subject
        book = self.chroma_client.get_collection(name=book_name)
        self.docs = book.query(query_texts=[query], n_results=3)





