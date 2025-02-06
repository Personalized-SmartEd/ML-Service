from fastapi import HTTPException
from src.Models.recommendation_engine import StudentProfile, StudyPlanRecommendation
from src.LLMs.deepseek_integration import GroqConfiguration, GroqRecommendationEngine


class RecommendationEngineService:
    def __init__(self):
        self.groq_config = GroqConfiguration()
        
    async def weekly_recommendation(self, profile: StudentProfile) -> StudyPlanRecommendation:
        try:
            engine = GroqRecommendationEngine(config=self.groq_config)
            plan = await engine.generate_recommendations(profile)
            return plan
        except ValueError as e:
            print(e)
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Failed to generate study plan")
