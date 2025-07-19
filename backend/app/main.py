from fastapi import FastAPI
from app.routes import test, transcription
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Diagnoassist API is running."}

app.include_router(test.router)
app.include_router(transcription.router)

