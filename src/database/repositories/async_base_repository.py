from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, List, Optional

from motor.core import AgnosticClientSession
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorClientSession
from bson import ObjectId

from pydantic import BaseModel

from src.utils.simple_result import SimpleResult, SimpleOkResult, SimpleErrorResult

ModelType = TypeVar("ModelType", bound=BaseModel)


class AsyncRepository(Generic[ModelType], ABC):
    def __init__(self, db: AsyncIOMotorDatabase, model: Type[ModelType], collection_name: str):
        self._db = db
        self._model = model
        self._collection_name = collection_name

    def collection(self) -> AsyncIOMotorCollection:
        return self._db[self._collection_name]

    async def insert(self, obj: ModelType, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[ModelType]:
        try:
            data = obj.model_dump(by_alias=True, exclude_none=True, exclude_unset=True,)
            result = await self.collection().insert_one(data, session=session)
            if result.acknowledged:
                obj.id = result.inserted_id
                return SimpleOkResult(payload=obj)
            return SimpleErrorResult("Insert not acknowledged")
        except Exception as e:
            return SimpleErrorResult(str(e))

    async def get_by_id(self, object_id: ObjectId, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[ModelType]:
        try:
            doc = await self.collection().find_one({"_id": object_id}, session=session)
            if not doc:
                return SimpleErrorResult(f"Document with id={object_id} not found")
            return SimpleOkResult(payload=self._model(**doc))
        except Exception as e:
            return SimpleErrorResult(str(e))

    async def find_all(self, filter_options: dict = dict(), session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[ModelType]]:
        try:
            cursor = self.collection().find(filter_options, session=session)
            items = [self._model(**doc) async for doc in cursor]
            return SimpleOkResult(payload=items)
        except Exception as e:
            return SimpleErrorResult(str(e))

    async def replace(self, object_id: ObjectId, obj: ModelType, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[bool]:
        try:
            data = obj.model_dump(by_alias=True)
            result = await self.collection().replace_one({"_id": object_id}, data, session=session)
            if result.matched_count:
                return SimpleOkResult(payload=True)
            return SimpleErrorResult(f"No document matched id={object_id}")
        except Exception as e:
            return SimpleErrorResult(str(e))

    async def update_one(self, obj: ModelType, session: AsyncIOMotorClientSession | None = None, upsert: bool = False) -> SimpleResult[bool]:
        try:
            obj_id = ObjectId(obj.id)
            new_obj = obj.model_copy(update={"_id": None})
            data = new_obj.model_dump(by_alias=True, exclude_none=True)
            result = await self.collection().update_one({"_id": obj_id}, data, session=session, upsert=upsert)
            if result.matched_count:
                return SimpleOkResult(payload=True)
            return SimpleErrorResult(f"No document matched id={obj_id}")
        except Exception as e:
            return SimpleErrorResult(str(e))

    async def delete(self, object_id: ObjectId, session: Optional[AgnosticClientSession] = None) -> SimpleResult[bool]:
        try:
            result = await self.collection().delete_one({"_id": object_id}, session=session)
            if result.deleted_count:
                return SimpleOkResult(payload=True)
            return SimpleErrorResult(f"No document deleted with id={object_id}")
        except Exception as e:
            return SimpleErrorResult(str(e))
