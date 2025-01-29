from fastapi import APIRouter

from src.Models.assessment import AssessmentResult, LearningStyleResult, PastScoresModel
from src.Models.quiz import QuizResponseModel, QuizSubmission
from src.Services.assessment import DynamicAssessmentService, InitialAssessmentService

router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"]
)

@router.get("/static", response_model=QuizResponseModel)
async def get_initial_quiz():
    service = InitialAssessmentService()  
    return await service.generate_initial_quiz()

@router.post("/static", response_model=LearningStyleResult)
async def get_initial_results(responses: QuizSubmission):
    service = InitialAssessmentService()
    return await service.process_results(responses)

@router.post("/dynamic", response_model=AssessmentResult)
async def get_dynamic_assessment(scores_data: PastScoresModel):
    service = DynamicAssessmentService()
    return  service.calculate_performance(scores_data.subject, scores_data.scores)