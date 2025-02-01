from pydantic import BaseModel

from Models.static_assessment import SubjectType

class Subject(BaseModel):
    subject: SubjectType
    chapter: str
    topic_description: str