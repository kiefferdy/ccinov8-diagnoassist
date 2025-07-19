from fastapi import FastAPI
from app.routes import test

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Diagnoassist API is running."}

app.include_router(test.router)

