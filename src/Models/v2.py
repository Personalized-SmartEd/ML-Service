from pydantic import BaseModel

class MindmapResponse(BaseModel):
    image_url: str
    mermaid_code: str