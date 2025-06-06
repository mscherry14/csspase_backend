from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.auth import get_current_user_tg_id, user_role_checker
from src.api.schemas.balance_schema import BalanceSchema
from src.api.schemas.shop.order_schema import OrderSchema
from src.api.schemas.shop.product_schema import ProductSchema
from src.api.schemas.transaction_schema import TransactionSchema
from src.database.models import UserRoles
from src.service.idempotency_key_service import idempotent
from src.service.orders_service import OrdersService
from src.service.shop_service import ShopService
from src.service.wallet_service import WalletService
from src.utils.simple_result import SimpleErrorResult
from src.database.database import db

ROLE = UserRoles.USER
router = APIRouter(prefix="/user", dependencies = [Depends(user_role_checker)])


@router.get("/balance", response_model=BalanceSchema)
async def get_balance(current_user_tg_id: int = Depends(get_current_user_tg_id)):
    """Получить баланс студента."""
    res = await WalletService(db=db).get_user_balance(user_id=current_user_tg_id)
    if isinstance(res, SimpleErrorResult):
        raise HTTPException(status_code=404, detail=res.message)
    return BalanceSchema(balance=res.payload)

@router.get("/transactions", response_model=List[TransactionSchema])
async def get_transactions(current_user_tg_id: int = Depends(get_current_user_tg_id)):
    """История транзакций студента."""
    res = await WalletService(db=db).get_user_transactions(user_id=current_user_tg_id)
    if isinstance(res, SimpleErrorResult):
        raise HTTPException(status_code=404, detail=res.message)
    res_list = [await TransactionSchema.users_from_transaction_db(user) for user in res.payload]
    return res_list[::-1]
#
# @router.get("/transactions/{transaction_id}")
# async def get_one_transaction(tg_id: str, limit: int = 10):
#     """"""
#     return


#TODO:вынести из /user??????
@router.get("/products", response_model=List[ProductSchema])
async def get_products():
    res = await ShopService(db=db).get_products_list()
    if isinstance(res, SimpleErrorResult):
        raise HTTPException(status_code=404, detail=res.message)
    return list(map(ProductSchema.model_validate,  map(lambda x: x.model_dump(), res.payload)))

#TODO:вынести из /user??????
@router.get("/products/{product_id}")
async def get_one_product(product_id: str):
    """Информация об одном товаре."""
    res = await ShopService(db=db).get_product_by_product_id(product_id)
    if isinstance(res, SimpleErrorResult):
        raise HTTPException(status_code=404, detail=res.message)
    return ProductSchema.model_validate(res.payload.model_dump())



@router.post("/orders/{product_id}", response_model=OrderSchema)
@idempotent
async def buy_product(product_id: str, request: Request, tg_id: int = Depends(get_current_user_tg_id)):
    res = await ShopService(db=db).buy_product(user_id=tg_id, product_id=product_id)
    if isinstance(res, SimpleErrorResult):
        raise HTTPException(status_code=402, detail=res.message)
    return OrderSchema.model_validate(res.payload.model_dump())


@router.get("/orders", response_model=List[OrderSchema])
async def get_orders(tg_id: int = Depends(get_current_user_tg_id)):
    """Список заказов студента."""
    res = await OrdersService(db=db).get_user_orders(user_id=tg_id)
    if isinstance(res, SimpleErrorResult):
        raise HTTPException(status_code=404, detail=res.message)
    res_list = list(map(OrderSchema.model_validate, map(lambda x: x.model_dump(), res.payload)))
    return res_list[::-1]