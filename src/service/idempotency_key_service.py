from functools import wraps
from typing import Callable, Awaitable, Any

from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import asyncio

from src.database.database import db
from src.database.models.idempotency_key import IdempotencyStatus, IdempotencyKeyDB
from src.database.repositories.idempotency_key_repository import IdempotencyKeyRepository
from src.utils.simple_result import SimpleErrorResult


def idempotent(handler: Callable[..., Awaitable[Any]]) -> Callable:
    @wraps(handler)
    async def wrapper(*args, request: Request, **kwargs):
        key = request.headers.get("Idempotency-Key")
        if not key:
            raise HTTPException(400, detail="Missing Idempotency-Key")

        record = await IdempotencyKeyRepository(db=db).find_one_by_key(key)

        if record:
            if record.status == IdempotencyStatus.PENDING:
                # Подождать (простой способ — sleep-loop)
                for _ in range(10):
                    await asyncio.sleep(0.5)
                    record = await IdempotencyKeyRepository(db=db).find_one_by_key(key)
                    if record.status != IdempotencyStatus.PENDING:
                        break
                else:
                    raise HTTPException(202, detail="Still processing, try again later")
            return record.response

        res = await IdempotencyKeyRepository(db=db).insert(IdempotencyKeyDB(
            key=key,
            status=IdempotencyStatus.PENDING,
            statusCode=202,
            response={"detail": "Still processing, try again later"},
            expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=5)
        ))
        if isinstance(res, SimpleErrorResult):
            raise HTTPException(500, detail="Internal server error: idempotency-key")
        record = res.payload

        try:
            result = await handler(*args, request=request, **kwargs)
            record.status = IdempotencyStatus.DONE
            record.response = result
            record.status_code = result.status_code if isinstance(result, Response) else 200
            await IdempotencyKeyRepository(db=db).update_one(record)
            return result
        except Exception as e:
            record.status = IdempotencyStatus.FAILED
            record.response = {"detail": str(e)}
            record.status_code = 500
            await IdempotencyKeyRepository(db=db).update_one(record)
            raise HTTPException(500, detail=str(e))

    return wrapper
