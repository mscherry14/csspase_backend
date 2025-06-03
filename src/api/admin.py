from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.auth import admin_role_checker
from src.api.schemas.shop.admin_order_schema import AdminOrderSchema
from src.api.schemas.shop.order_schema import OrderSchema
from src.api.schemas.shop.product_patch_schema import ProductPatchSchema
from src.api.schemas.shop.product_put_schema import ProductPutSchema
from src.api.schemas.shop.product_schema import ProductSchema
from src.api.user import get_products, get_one_product
from src.database.models.shop.order import OrderStatus
from src.database.repositories.shop.orders_repository import OrdersRepository
from src.service.orders_service import OrdersService
from src.database.database import db
from src.service.shop_service import ShopService
from src.utils.simple_result import SimpleOkResult

router = APIRouter(prefix="/admin")#, dependencies = [Depends(admin_role_checker)])


router.add_api_route("/products", get_products, methods=["GET"])
router.add_api_route("/products/{product_id}", get_one_product, methods=["GET"])

@router.post("/products", response_model=ProductSchema)
async def create_product(product: ProductSchema):
    """Добавить товар."""
    try:
        res = await ShopService(db=db).create_product(
            product_id=product.productId,
            price=product.price,
            title=product.title,
            photo=product.photo)
        return ProductSchema.model_validate(res.model_dump())
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) #TODO: norm exception

@router.put("/products/{product_id}", response_model=ProductSchema)
async def update_product(product_id: str, product: ProductPutSchema):
    """Обновить товар (перезаписать)"""
    try:
        res = await ShopService(db=db).update_product(
            product_id=product_id,
            price=product.price,
            title=product.title,
            photo=product.photo)
        return ProductSchema.model_validate(res.model_dump())
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))  # TODO: norm exception

@router.patch("/products/{product_id}", response_model=ProductSchema)
async def patch_product(product_id: str, product: ProductPatchSchema):
    """Обновить товар (по полям, можно поменять productId)"""
    try:
        res = await ShopService(db=db).patch_product(
            cur_product_id = product_id,
            product_id=product.productId,
            price=product.price,
            title=product.title,
            photo=product.photo)
        return ProductSchema.model_validate(res.model_dump())
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))  # TODO: norm exception


@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Удалить товар."""
    try:
        await ShopService(db=db).delete_product(product_id=product_id)
        return
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/orders", response_model=list[AdminOrderSchema])
async def get_orders(user: Optional[str] = None, status: Optional[str] = None):
    """Все заказы (админ)/с фильтром по пользователю"""
    try:
        res = await OrdersService(db=db).admin_get_orders(
            user_id=int(user) if user is not None else None,
            status=status
        )
        res_list = list(map(AdminOrderSchema.model_validate, map(lambda x: x.model_dump(), res)))
        return res_list[::-1]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/orders/{order_id}", response_model=list[AdminOrderSchema])
async def get_orders(order_id: str, status: Optional[str] = None):
    """Конкретный заказ"""
    try:
        res = await OrdersRepository(db=db).order_by_order_id(order_id=order_id)
        if isinstance(res, SimpleOkResult):
            order = AdminOrderSchema.model_validate(res.payload.model_dump())
            return order
        else:
            raise HTTPException(status_code=404, detail=res.message)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/orders/{order_id}/confirm")
async def confirm_order_status(order_id: str):
    """Изменить статус заказа на "подтвержден\""""
    try:
        res = await (OrdersService(db=db).order_set_status(order_id=order_id, status=OrderStatus.confirmed))
        order = AdminOrderSchema.model_validate(res.model_dump())
        return order
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/orders/{order_id}/cancel")
async def canceled_order_status(order_id: str):
    """Изменить статус заказа на "отменен\""""
    try:
        res = await (OrdersService(db=db).order_set_status(order_id=order_id, status=OrderStatus.canceled))
        order = AdminOrderSchema.model_validate(res.model_dump())
        return order
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/orders/{order_id}/complete")
async def completed_order_status(order_id: str):
    """Изменить статус заказа на "завершен\""""
    try:
        res = await (OrdersService(db=db).order_set_status(order_id=order_id, status=OrderStatus.completed))
        order = AdminOrderSchema.model_validate(res.model_dump())
        return order
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

