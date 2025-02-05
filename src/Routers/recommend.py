from fastapi import APIRouter, Depends, HTTPException

from src.LLMs.deepseek_integration import GroqConfiguration, get_groq_config
from src.Models.recommendation_engine import StudentProfile, StudyPlanRecommendation
from src.Services.reccomendation_engine import GroqRecommendationEngine, RecommendationEngineService

router = APIRouter(
    prefix="/reccomend",
    tags=["Reccomendation Engine"]
)
service = RecommendationEngineService()

@router.post("/generate_study_plan/", response_model=StudyPlanRecommendation, summary="Generate personalized study plan",)
async def generate_study_plan( profile: StudentProfile ):
    return await service.weekly_recommendation(profile)