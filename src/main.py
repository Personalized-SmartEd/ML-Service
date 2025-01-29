from fastapi import FastAPI
from src.Routers import assessment

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "healthy"}

app.include_router(assessment.router)