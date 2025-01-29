from fastapi import APIRouter

from src.Models.learning_style import LearningStyleResult
from src.Models.quiz import QuizResponseModel, QuizSubmission
from src.Services.assessment import InitialAssessmentService

router = APIRouter(
    prefix="/assessment",
    tags=["assessment"]
)

@router.get("/", response_model=QuizResponseModel)
async def get_initial_quiz():
    service = InitialAssessmentService()  
    return await service.generate_initial_quiz()

@router.post("/", response_model=LearningStyleResult)
async def get_initial_results(responses: QuizSubmission):
    service = InitialAssessmentService()
    return await service.process_results(responses)
