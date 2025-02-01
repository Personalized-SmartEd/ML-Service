from fastapi import APIRouter

from src.Models.doubt_bot import DoubtBotRequest, DoubtBotResponse
from src.Services.doubt_bot import DoubtBotService


router = APIRouter(prefix="/doubt", tags=['Doubt bot'])
service = DoubtBotService()

@router.post("/ask", response_model=DoubtBotResponse)
async def ask_doubt(request: DoubtBotRequest):
    return await service.solve_doubt(request)