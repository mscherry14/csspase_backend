from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

from src.api.auth import router as auth_router
from src.api.user import router as user_router
from src.api.teacher import router as teacher_router
from src.api.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse
import httpx

from src.config import settings
from src.database.database import db
from src.database.repositories.idempotency_key_repository import IdempotencyKeyRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    await IdempotencyKeyRepository(db=db).setup_index()
    yield
    db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=[settings.ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(teacher_router)
app.include_router(admin_router)


@app.get("/")
async def read_root():
    return JSONResponse(status_code=200,content={})
@app.get("/proxy-image")
async def proxy_image(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return StreamingResponse(
                response.iter_bytes(),
                media_type=response.headers.get("content-type"),
            )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch image")
