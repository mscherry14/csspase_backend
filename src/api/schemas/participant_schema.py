from src.api.schemas.user_schema import UserSchema
from src.database.models import UserDB


#TODO: implement
class ParticipantSchema(UserSchema):
    send: int = 0

    @staticmethod
    def from_user_db(user: UserDB):
        return ParticipantSchema(
            id=str(user.tg_id), # ????? maybe tg_id int
            name=user.name
        )