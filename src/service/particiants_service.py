from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from src.database.models import UserDB
from src.database.models.banking.utils import TransferStatus
from src.database.repositories.banking.event_banking_accounts_repository import EventBankingAccountsRepository
from src.database.repositories.banking.event_to_user_payments_repository import EventToUserPaymentsRepository
from src.database.repositories.banking.user_banking_accounts_repository import UserBankingAccountsRepository
from src.database.repositories.team_repository import TeamsRepository
from src.database.repositories.users_repository import UsersRepository
from src.service.event_service import EventServiceException
from src.service.models.event import EventModel, EventType
from src.utils.simple_result import SimpleOkResult, SimpleResult, SimpleErrorResult

class ParticipantsServiceException(Exception):
    pass

class ParticipantsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def extend_participant(self, participant_id: int, event_id: str,
                            session: AsyncIOMotorClientSession | None = None) -> int:
        """
        Returns how many tokens was sent to participant in this event
        """
        res = await EventBankingAccountsRepository(db=self.db).get_account_by_event_id(event_id=event_id,
                                                                                       session=session)
        # get event banking account info
        if isinstance(res, SimpleErrorResult):
            raise Exception("event banking account error")
        event_account = res.payload.accountId
        res = await UserBankingAccountsRepository(db=self.db).get_account_by_user_id(user_id=participant_id,
                                                                                       session=session)
        # get event banking account info
        if isinstance(res, SimpleErrorResult):
            raise Exception("user banking account error")
        user_account = res.payload.accountId
        amount = 0
        result = await EventToUserPaymentsRepository(db=self.db).get_payments_by_filter(from_event_id=event_account, to_user_id=user_account, status=TransferStatus.completed, session=session)
        if isinstance(res, SimpleErrorResult):
            raise Exception("money transfer service error")
        for payment in result.payload:
            amount += payment.amount
        return amount


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