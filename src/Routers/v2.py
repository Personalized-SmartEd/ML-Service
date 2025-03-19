from fastapi import APIRouter, HTTPException
from src.Models.v2 import MindmapResponse
from src.Services.v2 import V2Service
from src.Services.v2_video import V2VideoServiceWrapper
from src.Models.v2_video import SummaryRequest, SummaryResponse

router = APIRouter(
    prefix="/v2",
    tags=["Version 2 for some additional features."]
)
service = V2Service()
service2 = V2VideoServiceWrapper()

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

@router.post("/summarize/youtube", response_model=SummaryResponse)
async def summarize_youtube_detailed(request: SummaryRequest):
    response = service2.summarize_youtube_video(request)
    return response
    
    
    
