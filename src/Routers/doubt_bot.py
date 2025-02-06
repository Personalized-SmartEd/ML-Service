from fastapi import APIRouter

from src.Models.doubt_bot import DoubtBotRequest, DoubtBotResponse
from src.Services.doubt_bot import  DoubtSolver


router = APIRouter(
    prefix="/doubt",
    tags=['Doubt bot']
)
service = DoubtSolver()

@router.post("/ask")
async def ask_doubt(request: DoubtBotRequest) -> DoubtBotResponse:
    return await service.doubt_solver(request)