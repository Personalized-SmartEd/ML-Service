from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from src.Models.student import Student
from src.Models.subject import Subject


class DoubtInput(BaseModel):
    text: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    image_description: Optional[str] = None

class VisualAnnotation(BaseModel):
    coordinates: List[float]  # [x1, y1, x2, y2] normalized coords
    explanation: str
    annotation_type: str  # "highlight", "circle", "arrow"

class DoubtBotRequest(BaseModel):
    student: Student  # Your existing Student model
    doubt: DoubtInput
    subject: Optional[Subject] = None  # Your existing Subject model

class DoubtBotResponse(BaseModel):
    explanation: str
    visual_annotations: List[VisualAnnotation] = []
    follow_up_questions: List[str] = []
