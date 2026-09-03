from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from api.cases import router as cases_router

load_dotenv()

app = FastAPI(title="TathyaAI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "TathyaAI",
        "version": "0.1.0"
    }