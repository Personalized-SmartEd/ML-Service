from pydantic import BaseModel
from typing import Optional

class VideoURL(BaseModel):
    url: str
    
class SummaryOptions(BaseModel):
    format: Optional[str] = "markdown"
    length: Optional[str] = "medium"
    language: Optional[str] = "english"
    
class SummaryRequest(BaseModel):
    url: str
    options: Optional[SummaryOptions] = SummaryOptions()
    
class SummaryResponse(BaseModel):
    id: str
    summary: str
    transcript: str
    metadata: dict