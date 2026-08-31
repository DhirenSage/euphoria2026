from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
from lib.db import client, db


# Startup runs before the yield, shutdown after it. Add your own setup/teardown here.
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()


# Create the main app without a prefix
app = FastAPI(lifespan=lifespan)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class EuphoriaHealth(BaseModel):
    ok: bool
    service: str
    timestamp: str

class EuphoriaEvent(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    short_description: str | None = None
    event_type: str
    registration_type: str
    fee: float
    capacity: int
    venue: str | None = None
    status: str
    category_name: str | None = None

class EuphoriaEventsMeta(BaseModel):
    programme: str

class EuphoriaEventsResponse(BaseModel):
    data: list[EuphoriaEvent]
    meta: EuphoriaEventsMeta

class EuphoriaEventResponse(BaseModel):
    data: EuphoriaEvent

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.model_dump())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

async def codeigniter_get(path: str) -> tuple[int, dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"http://localhost:3000/api/{path}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="CodeIgniter returned an invalid response") from exc
    return response.status_code, payload

@api_router.get("/health", response_model=EuphoriaHealth)
async def euphoria_health():
    status, payload = await codeigniter_get("health")
    if status != 200:
        raise HTTPException(status_code=502, detail="Euphoria service unavailable")
    return payload

@api_router.get("/events", response_model=EuphoriaEventsResponse)
async def euphoria_events():
    status, payload = await codeigniter_get("events")
    if status != 200:
        raise HTTPException(status_code=502, detail="Euphoria events unavailable")
    return payload

@api_router.get("/events/{slug}", response_model=EuphoriaEventResponse)
async def euphoria_event(slug: str):
    status, payload = await codeigniter_get(f"events/{slug}")
    if status == 404:
        return JSONResponse(status_code=404, content=payload)
    if status != 200:
        raise HTTPException(status_code=502, detail="Euphoria event unavailable")
    return payload

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Include the router last so every /api route above is registered.
app.include_router(api_router)
