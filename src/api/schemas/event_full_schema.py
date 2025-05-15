from typing import List
from pydantic import EmailStr, Field
from src.api.schemas.event_short_schema import EventShortSchema
from src.api.schemas.person_schema import PersonSchema
from src.database.database import db
from src.service.models.extended_event import ExtendedEventModel
from src.service.teacher_event_service import TeacherEventService


class EventFullSchema(EventShortSchema):
    speakers: List[PersonSchema] = Field(default=list)

    @staticmethod
    async def from_extended_event(event: ExtendedEventModel) -> "EventFullSchema":
        new_speakers: List[PersonSchema] = list()
        for speaker in event.speakers:
            new_speakers.append(PersonSchema.from_person(await TeacherEventService(db=db).get_user_from_email(user_mail=speaker)))
        return EventFullSchema(
            eventId=event.eventId,
            title=event.title,
            type=event.type,
            shortDescription=event.shortDescription,
            speakers=new_speakers,
            tags=event.tags,
            dateTags=event.dateTags,
            registrationDeadline=event.registrationDeadline,
            registrationLink=event.registrationLink,
            balance=event.balance,
            init_balance=event.init_balance,
        )