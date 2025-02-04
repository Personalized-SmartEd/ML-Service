from fastapi import APIRouter, HTTPException

from src.Models.tutor_bot import TutorSessionRequest, TutorSessionResponse
from src.Services.tutor_bot import TutorBotService

router = APIRouter(
    prefix="/tutor",
    tags=["Tutor Bot"]
)
service = TutorBotService()

@router.post("/session", response_model=TutorSessionResponse)
async def get_tutor_session(request: TutorSessionRequest):
    return await service.generate_tutor_response(request)

@router.get("/classes", summary="List available classes and subjects")
def list_classes():
    class_subject_map = service.get_available_classes_subjects()
    return class_subject_map