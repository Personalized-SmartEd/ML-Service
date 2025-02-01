from pydantic import BaseModel

from src.Models.static_assessment import SubjectType

class Subject(BaseModel):
    subject: SubjectType
    chapter: str
    topic_description: str