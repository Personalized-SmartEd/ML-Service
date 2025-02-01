from pydantic import BaseModel

from src.Models.static_assessment import LearningStyleType, PerformanceLevel

class Student(BaseModel):
    student_class: int
    student_performance_from_1_to_100: int
    student_learning_style: LearningStyleType
    student_performance_level: PerformanceLevel

