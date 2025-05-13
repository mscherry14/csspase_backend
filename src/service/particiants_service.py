from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from src.database.models import UserDB
from src.database.repositories.team_repository import TeamsRepository
from src.database.repositories.users_repository import UsersRepository
from src.service.models.event import EventModel, EventType
from src.utils.simple_result import SimpleOkResult, SimpleResult, SimpleErrorResult

class ParticipantsServiceException(Exception):
    pass

class ParticipantsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_event_participants(self, event: EventModel, session: AsyncIOMotorClientSession | None = None) -> List[UserDB]:
        res : SimpleResult[List[UserDB]] = SimpleOkResult(payload=list())
        match event.type:
            case EventType.open_lecture:
                res = await UsersRepository(db=self.db).get_open_lecture_participants(open_lecture_id=event.eventId, session=session)
            case EventType.course:
                res = await UsersRepository(db=self.db).get_course_participants(course_id=event.eventId, session=session)
            case EventType.competition:
                result = await TeamsRepository(db=self.db).get_competition_teams(competition_id=event.eventId, session=session)
                if isinstance(result, SimpleErrorResult):
                    raise ParticipantsServiceException(result.message)
                participants = list()
                for team in result.payload:
                    for member in team.members:
                        res_user = await UsersRepository(db=self.db).get_by_user_id(user_id=int(member), session=session)
                        if isinstance(res_user, SimpleErrorResult):
                            raise ParticipantsServiceException(res_user.message)
                        participants.append(res_user.payload)
                res = SimpleOkResult(payload=participants)
            case EventType.school:
                res = await UsersRepository(db=self.db).get_school_participants(school_id=event.eventId, session=session)
        if isinstance(res, SimpleErrorResult):
            raise ParticipantsServiceException(res.message)
        return res.payload