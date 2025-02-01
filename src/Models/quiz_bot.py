from pydantic import BaseModel

from src.Models.base_subject import Subject
from src.Models.base_student import Student

class QuizInfo(BaseModel):
    quiz_difficulty_from_1_to_10: int
    quiz_duration_minutes: int
    number_of_questions: int

class QuizRequestBody(BaseModel):
    student_info : Student
    subject_info : Subject
    quiz_info : QuizInfo