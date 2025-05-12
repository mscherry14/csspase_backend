import re

from bson import ObjectId
from pydantic import BaseModel, AfterValidator, GetCoreSchemaHandler
from typing import Literal, Annotated, Any

from pydantic_core import core_schema


class TVideo(BaseModel):
    source: Literal["youtube", "rutube", "vk", "other"]
    url: str  # HttpUrl from pydantic


class ExtraMaterial(BaseModel):
    title: str
    url: str  # HttpUrl from pydantic


class SimmiliarEvent(BaseModel):
    tag: str
    eventId: str

def strip_control_chars(s: str) -> str:
    """
    Удаляет недопустимые управляющие символы из строки (кроме \n, \r, \t).
    """
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', s.replace('\u2028', '\n').replace('\u2029', '\n'))

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        def validate(v):
            if isinstance(v, dict) and "$oid" in v:
                v = v["$oid"]
            if isinstance(v, str):
                return ObjectId(v)
            if isinstance(v, ObjectId):
                return v
            raise ValueError("Invalid ObjectId")

        def serialize(v: ObjectId):
            return {"$oid": str(v)}

        return core_schema.json_or_python_schema(
            python_schema=core_schema.no_info_plain_validator_function(validate),
            json_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.plain_serializer_function_ser_schema(serialize)
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string", "format": "objectid"}