from fastapi import HTTPException, Depends, status, APIRouter
from jose import JWTError
from pydantic import BaseModel

from src.database.database import db
from src.database.models import UserDB
from src.database.repositories.auth.refresh_token_repository import RefreshTokensRepository
from src.database.repositories.users_repository import UsersRepository
from src.service.auth.jwt import decode_token, create_access_token, create_refresh_token
from fastapi.security import OAuth2PasswordBearer

from src.utils.simple_result import SimpleErrorResult

router = APIRouter(prefix="/auth")#, dependencies=[Depends(AuthService.check_teacher_role)])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        username: int = int(payload.get("sub")) #TODO: get real cred
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UsersRepository(db=db).get_by_user_id(user_id=username) # Ваша функция получения пользователя
    if (user is None) or isinstance(user, SimpleErrorResult):
        raise credentials_exception
    return user.payload

@router.get("/me/id", response_model=int)
async def read_me(current_user: UserDB = Depends(get_current_user)):
    return current_user.tg_id


@router.post("/token", response_model=Token)
async def login():
    access_token = create_access_token(
        data={"sub": "123456789"},
    )
    ref_token = await create_refresh_token(
        data={"sub": "123456789"},
    )
    return Token(
        access_token=access_token,
        refresh_token=ref_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refr_token: str = Depends(oauth2_scheme)):
    payload = decode_token(refr_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    username = payload.get("sub")
    if int(username) != 123456789:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    new_access_token = create_access_token(
        data={"sub": 123456789,}
    )
    new_refresh_token = await create_refresh_token(
        data={"sub": 123456789, }
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

@router.get("/me", response_model=UserDB)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

@router.get("/me/test")
async def all_refresh():
    res = await RefreshTokensRepository(db=db).find_all()
    print(res.payload[1].model_dump_json())
    return {}
