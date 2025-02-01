from fastapi import APIRouter

from src.Models.static_assessment import AssessmentResult, LearningStyleResult, PastScoresModel
from src.Models.dynamic_assessment import QuizResponseModel, QuizSubmission
from src.Services.assessment import DynamicAssessmentService, InitialAssessmentService

router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"]
)
static_service = InitialAssessmentService() 
dynamic_service = DynamicAssessmentService()

# Routes
@router.get("/static", response_model=QuizResponseModel)
async def get_initial_quiz():
    return await static_service.generate_initial_quiz()

@router.post("/static", response_model=LearningStyleResult)
async def get_initial_results(responses: QuizSubmission):
    return await static_service.process_results(responses)

@router.post("/dynamic", response_model=AssessmentResult)
async def get_dynamic_assessment(scores_data: PastScoresModel):
    return  dynamic_service.calculate_performance(scores_data.subject, scores_data.scores)