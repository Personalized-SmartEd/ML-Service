from typing import List

from pydantic import BaseModel

from Models.base_student import Student
from Models.base_subject import Subject

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