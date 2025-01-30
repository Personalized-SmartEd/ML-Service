from pydantic import BaseModel

from src.Models.assessment import SubjectType

class QuizRequestBody(BaseModel):
    # student - info
    student_class: int
    student_performance: int
    student_learning_style: str
    student_pace: str

    # subject info
    subject: SubjectType
    chapter: str
    topic_description: str

    # quiz info
    quiz_difficulty: int
    quiz_duration_minutes: int
    number_of_questions: int