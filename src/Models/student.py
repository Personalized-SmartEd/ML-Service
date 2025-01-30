from pydantic import BaseModel

class Student(BaseModel):
    student_class: int
    student_performance: int
    student_learning_style: str
    student_pace: str

