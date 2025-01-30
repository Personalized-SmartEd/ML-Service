from typing import List

from pydantic import BaseModel

from src.Models.chat import ChatMessage
from src.Models.student import Student
from src.Models.subject import Subject

class TutorSessionRequest(BaseModel):
    subject: Subject
    student: Student
    chat_history: List[ChatMessage]
    new_message: str

class TutorSessionResponse(BaseModel):
    explanation: str
    updated_chat_history: List[ChatMessage]