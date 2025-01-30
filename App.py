import uvicorn
from src.main import app
from dotenv import load_dotenv
import os  

load_dotenv('.env')
PORT = os.getenv('PORT')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT or 8000)