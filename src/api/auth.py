from typing import List

from fastapi import HTTPException, Depends, status, APIRouter, Body
from jose import JWTError
from pydantic import BaseModel

from src.api.schemas.telegram_auth_schema import TelegramAuthSchema
from src.database.database import db
from src.database.models import UserDB, PersonRole, UserRoles
from src.database.repositories.users_repository import UsersRepository
from src.service.auth.jwt import decode_token, create_access_token, create_refresh_token
from fastapi.security import OAuth2PasswordBearer

from src.service.auth.telegram_auth import check_webapp_signature, get_user_id
from src.utils.simple_result import SimpleErrorResult

router = APIRouter(prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/tg_login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDB:
    try:
        payload = decode_token(token)
        if not payload:
            raise credentials_exception
        user_id: int = int(payload.get("sub"))  # TODO: get real cred
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UsersRepository(db=db).get_by_user_id(user_id=user_id)
    if (user is None) or isinstance(user, SimpleErrorResult):
        raise credentials_exception
    return user.payload


async def get_tokens(user: UserDB) -> Token:
    # data for token
    data = {
        "sub": str(user.tg_id),
        "tg_id": user.tg_id,
        "roles": user.roles
    }

    # token creating
    access_token = create_access_token(
        data=data,
    )
    ref_token = await create_refresh_token(
        data=data,
    )
    return Token(
        access_token=access_token,
        refresh_token=ref_token
    )


@router.post("/tg_login", response_model=Token)
async def telegram_login(payload: TelegramAuthSchema = Body()):
    # verify user
    if not check_webapp_signature(payload.init_data):
        raise credentials_exception
    # get user
    user_id = get_user_id(payload.init_data)
    user = await UsersRepository(db=db).get_by_user_id(user_id=user_id)
    if (user is None) or isinstance(user, SimpleErrorResult):
        raise credentials_exception
    return await get_tokens(user.payload)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh: str = Depends(oauth2_scheme)):
    payload = decode_token(refresh)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    user = await get_current_user(refresh)
    return await get_tokens(user)


@router.get("/me", response_model=UserDB)
async def get_my_user_info(current_user: UserDB = Depends(get_current_user)):
    return current_user


@router.get("/me/id", response_model=int)
async def get_current_user_tg_id(current_user: UserDB = Depends(get_current_user)):
    return current_user.tg_id


@router.get("/me/roles", response_model=List[UserRoles])
async def get_my_roles(current_user: UserDB = Depends(get_current_user)):
    return current_user.roles

def user_role_checker(current_user: UserDB = Depends(get_current_user)):
    if UserRoles.USER not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action: role " + UserRoles.USER + " needed"
        )
    return None

def teacher_role_checker(current_user: UserDB = Depends(get_current_user)):
    if UserRoles.TEACHER not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action: role " + UserRoles.TEACHER + " needed"
        )
    return None
def admin_role_checker(current_user: UserDB = Depends(get_current_user)):
    if UserRoles.ADMIN not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action: role " + UserRoles.ADMIN + " needed"
        )
    return None

#TODO: REMOVE AFTER TEST WRITTEN
@router.post("/test_login", response_model=Token)
async def test_login():
    # # verify user
    # if not check_webapp_signature(payload.init_data):
    #     raise credentials_exception
    # get user
    user_id = 123456789
    user = await UsersRepository(db=db).get_by_user_id(user_id=user_id)
    if (user is None) or isinstance(user, SimpleErrorResult):
        raise HTTPException(status_code=400, detail=f"you db suck: {user.message}")#credentials_exception
    return await get_tokens(user.payload)

@router.post("/test_login_gg", response_model=Token)
async def test_login():
    # # verify user
    # if not check_webapp_signature(payload.init_data):
    #     raise credentials_exception
    # get user
    user_id = 1111111111
    user = await UsersRepository(db=db).get_by_user_id(user_id=user_id)
    if (user is None) or isinstance(user, SimpleErrorResult):
        raise credentials_exception
    return await get_tokens(user.payload)
