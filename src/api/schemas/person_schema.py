from src.api.schemas.user_schema import UserSchema
from src.database.models import PersonRole, PersonDB


class PersonSchema(UserSchema):
    photo: str
    role: PersonRole

    @staticmethod
    def from_person(person: PersonDB) -> "PersonSchema":
        return PersonSchema(
            id=str(person.tg_id),
            name=person.firstName + " " + person.lastName,
            role=person.role,
            photo=person.photo,
        )