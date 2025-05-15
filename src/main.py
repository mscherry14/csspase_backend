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
    repo = PeopleRepository(db=db)
    try:
        await add_fake_users()
        print(await get_all_persons(repo))
        print('success')
        return JSONResponse(status_code=200, content={})
    except ValidationError as e:
        print('error')
        print(e.errors())
        return JSONResponse(status_code=400,content={})
    except Exception as e:
        print('not validation error: {}'.format(e))
        return JSONResponse(status_code=400,content={})


async def get_all_persons(repo) -> List[PersonDB]:
    # Используем асинхронный запрос для получения всех записей
    res = await repo.find_all()
    print(res.__class__)
    if isinstance(res, SimpleOkResult):
        return res.payload
    else:
        print(res.message)
        raise Exception(res.message)
