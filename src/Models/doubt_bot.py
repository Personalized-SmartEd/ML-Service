from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from src.Models.static_assessment import SubjectType
from src.Models.base_student import Student
from src.Models.base_subject import Subject


class DoubtInput(BaseModel):
    question: str
    # if image doubt
    image_url: Optional[HttpUrl] = None
    image_description: Optional[str] = None

class DoubtBotRequest(BaseModel):
    student: Student  
    doubt: DoubtInput
    subject: SubjectType

class DoubtBotResponse(BaseModel):
    explanation: str
    keypoints: List[str]
    follow_up_questions: List[str]
