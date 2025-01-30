from fastapi import APIRouter

from src.Models.tutor_bot import TutorSessionRequest, TutorSessionResponse
from src.Services.tutor_bot import TutorBotService

router = APIRouter(
    prefix="/tutor",
    tags=["Tutor Bot"]
)

@router.post("/session", response_model=TutorSessionResponse)
async def get_quiz(request: TutorSessionRequest):
    return await TutorBotService().generate_tutor_response(request)

