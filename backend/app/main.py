from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from dotenv import load_dotenv
import os

from app.api.endpoints import chat, dashboard
from app.services.retriever import retriever
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute heavy FAISS initialization when the server boots
    print("Pre-loading FAISS Database into memory...")
    if not retriever.is_ready:
        retriever.load()
    print("FAISS Initialized!")
    yield

app = FastAPI(
    title="Dekho API",
    description="Backend for Dekho — a habit-first personal finance companion",
    version="0.1.0",
    lifespan=lifespan,
)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "message": "Dekho API is running"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
