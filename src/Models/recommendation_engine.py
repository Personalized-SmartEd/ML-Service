from typing import List
from pydantic import BaseModel


class StudyRecommendation(BaseModel):
    resources: List[str]
    learning_path: List[str]
    estimated_time: str