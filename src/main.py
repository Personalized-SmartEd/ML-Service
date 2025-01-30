from fastapi import FastAPI
from src.Routers import assessment, quiz_bot

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "healthy"}

app.include_router(assessment.router)
app.include_router(quiz_bot.router)