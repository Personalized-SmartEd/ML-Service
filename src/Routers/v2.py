from fastapi import APIRouter

from src.Models.v2 import MindmapResponse
from src.Services.v2 import V2Service

router = APIRouter(
    prefix="/v2",
    tags=["Version 2 for some additional features."]
)
service = V2Service()

@router.get("/status")
async def get_status():
    return {"status": "v2 api is up and running!"}

@router.post("/summarise/")
async def summarise_pdf(pdf_url: str) -> str:
    return service.summarise_pdf(pdf_url)

@router.post("/summarise-youtube/")
async def summarise_youtube(youtube_url: str) -> str:
    return service.summarise_youtube(youtube_url)

@router.post("/generate_mindmap/{topic}")
async def generate_mindmap(topic: str) -> MindmapResponse:
    return service.generate_mindmap(topic)
    
