from typing import List

from pydantic import BaseModel

from src.Models.base_student import Student
from src.Models.base_subject import Subject

class ChatMessage(BaseModel):
    content: str
    sender: str  # "student" or "tutor"

class TutorSessionRequest(BaseModel):
    subject: Subject
    student: Student
    chat_history: List[ChatMessage]
    new_message: str

class TutorSessionResponse(BaseModel):
    explanation: str
    updated_chat_history: List[ChatMessage]
    follow_up_questions: List[str]
    key_points: List[str]
    docs: dict