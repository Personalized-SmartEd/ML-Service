from fastapi import APIRouter, Depends, HTTPException

from src.LLMs.deepseek_integration import GroqConfiguration, get_groq_config
from src.Models.recommendation_engine import StudentProfile, StudyPlanRecommendation
from src.Services.reccomendation_engine import GroqRecommendationEngine

router = APIRouter(
    prefix="/reccomend",
    tags=["Reccomendation Engine"]
)

@router.post("/generate_study_plan/", response_model=StudyPlanRecommendation, summary="Generate personalized study plan",)
async def generate_study_plan(
    profile: StudentProfile,
    groq_config: GroqConfiguration = Depends(get_groq_config)
):
    try:
        engine = GroqRecommendationEngine(config=groq_config)
        plan = await engine.generate_recommendations(profile)
        return plan
    except ValueError as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to generate study plan")