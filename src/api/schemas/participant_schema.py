from motor.motor_asyncio import AsyncIOMotorClientSession

from src.api.schemas.user_schema import UserSchema
from src.database.database import db
from src.database.models import UserDB
from src.service.particiants_service import ParticipantsService


#TODO: implement
class ParticipantSchema(UserSchema):
    sent: int = 0

    @staticmethod
    async def from_user_db(user: UserDB, event_id: str,):
        try:
            send = await ParticipantsService(db=db).extend_participant(user.tg_id, event_id)
        except Exception as e:
            send = 0
        return ParticipantSchema(
            id=str(user.tg_id), # ????? maybe tg_id int
            name=user.name,
            sent=send,
        )