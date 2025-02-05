from fastapi import APIRouter
from src.Models.recommendation_engine import StudentProfile, StudyPlanRecommendation
from src.Services.reccomendation_engine import RecommendationEngineService

router = APIRouter(
    prefix="/reccomend",
    tags=["Reccomendation Engine"]
)
service = RecommendationEngineService()

@router.post("/generate_study_plan/", response_model=StudyPlanRecommendation, summary="Generate personalized study plan",)
async def generate_study_plan( profile: StudentProfile ):
    return await service.weekly_recommendation(profile)