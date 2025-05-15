from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from starlette.responses import JSONResponse

from add_fake_users import add_fake_users
from src.api.auth import router as auth_router
from src.api.user import router as user_router
from src.api.teacher import router as teacher_router
from src.api.admin import router as admin_router
from src.database.database import db
from src.database.models import PersonDB
from src.database.repositories.people_repository import PeopleRepository
from src.utils.simple_result import SimpleOkResult

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(teacher_router)
# app.include_router(admin_router)
@app.get("/")
async def read_root():
    return JSONResponse(status_code=200,content={})
