from fastapi import APIRouter

from src.Services.quiz_bot import QuizBotService
from src.Models.dynamic_assessment import QuizResponseModel
from src.Models.quiz_bot import QuizRequestBody

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz Bot"]
)
service = QuizBotService()

@router.post("/", response_model=QuizResponseModel)
async def get_quiz(request: QuizRequestBody):
    return await service.get_quiz(request)

