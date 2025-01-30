from fastapi import APIRouter

from src.Services.quiz_bot import QuizBotService
from src.Models.quiz import QuizResponseModel
from src.Models.quiz_bot import QuizRequestBody

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz Bot"]
)

@router.post("/", response_model=QuizResponseModel)
async def get_quiz(request: QuizRequestBody):
    return await QuizBotService().get_quiz(request)

