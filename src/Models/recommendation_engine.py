from enum import Enum
import os
from typing import Dict, List
from pydantic import BaseModel, Field, HttpUrl, field_validator

from src.Models.base_student import Pace
from src.Models.static_assessment import LearningStyleType, PerformanceLevel


class ResourceFormat(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    AUDIO = "audio"
    WEB = "web"

class Resource(BaseModel):
    type: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    format: ResourceFormat
    topics: List[str] = Field(..., min_items=1)
    match_style: LearningStyleType
    link: HttpUrl

class DailySchedule(BaseModel):
    day: str
    subjects: List[str]
    duration: float = Field(..., gt=0)
    activities: List[str]

class ExercisePlan(BaseModel):
    type: str
    target: str
    difficulty: PerformanceLevel

class StudyPlanRecommendation(BaseModel):
    weekly_schedule: List[DailySchedule]
    study_resources: List[Resource]
    time_allocation: Dict[str, float]
    exercise_plan: List[ExercisePlan]
    progress_predictions: Dict[str, float]

class StudentProfile(BaseModel):
    learning_style: LearningStyleType
    current_level: PerformanceLevel
    weak_areas: List[str] = Field(..., min_items=1, max_items=5)
    performance_history: List[float] = Field(..., min_items=1)
    preferred_pace:  Pace
    available_hours: int = Field(..., gt=0, le=168)

    @field_validator('performance_history')
    def validate_performance_scores(cls, v):
        if not all(0 <= score <= 100 for score in v):
            raise ValueError("Performance scores must be between 0 and 100")
        return v