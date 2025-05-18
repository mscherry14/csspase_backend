from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

from src.api.auth import router as auth_router
from src.api.user import router as user_router
from src.api.teacher import router as teacher_router
from src.api.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["http://localhost:62427"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(teacher_router)
# app.include_router(admin_router)
@app.get("/")
async def read_root():
    return JSONResponse(status_code=200,content={})
