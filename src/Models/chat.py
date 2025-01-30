from typing import List

from pydantic import BaseModel

from src.Models.student import Student
from src.Models.subject import Subject


# --- Chat Models ---
class ChatMessage(BaseModel):
    content: str
    sender: str  # "student" or "tutor"