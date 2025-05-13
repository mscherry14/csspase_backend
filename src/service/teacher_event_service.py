from typing import List

from motor.motor_asyncio import AsyncIOMotorClientSession

from src.database.models import UserRoles, PersonDB
from src.database.models.banking.event_to_user_payment import EventToUserPaymentDB
from src.database.models.banking.utils import TransferStatus
from src.database.repositories.banking.event_banking_accounts_repository import EventBankingAccountsRepository
from src.database.repositories.banking.event_to_user_payments_repository import EventToUserPaymentsRepository
from src.database.repositories.banking.user_banking_accounts_repository import UserBankingAccountsRepository
from src.database.repositories.competitions_repository import CompetitionsRepository
from src.database.repositories.courses_repository import CoursesRepository
from src.database.repositories.open_lectures_repository import OpenLecturesRepository
from src.database.repositories.people_repository import PeopleRepository
from src.database.repositories.school_repository import SchoolsRepository
from src.database.repositories.users_repository import UsersRepository
from src.service.event_service import EventServiceException, EventService
from src.service.models.event import EventModel
from src.service.models.extended_event import ExtendedEventModel
from src.service.money_transfer_service import MoneyTransferService
from src.service.particiants_service import ParticipantsService
from src.utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class TeacherEventService:
    def __init__(self, db):
        self.db = db
        self.opelLecturesRepository = OpenLecturesRepository(self.db)
        self.coursesRepository = CoursesRepository(self.db)
        self.schoolsRepository = SchoolsRepository(self.db)
        self.competitionsRepository = CompetitionsRepository(self.db)

    # async def _get_user_from_email(self, user_mail: EmailStr):
    #     res = await PeopleRepository(db=db).get_by_email(mail=user_mail)
    #     if res is None:
    #         raise EventServiceException("no user with such mail found")
    #     user_id = res.payload.tg_id
    #     if not user_id:
    #         raise EventServiceException("no tg-bot user with such mail found")
    #     result = await UsersRepository(db=db).get_by_user_id(user_id)
    #     if result is None:
    #         raise EventServiceException("no user with such tg_id found")
    #     if not UserRoles.TEACHER in result.payload.roles:
    #         raise EventServiceException("incorrect role. please contact with administrator")
    #     return result.payload

    async def _get_user_from_tg_id(self, user_id: int) -> PersonDB:
        # verify role
        result = await UsersRepository(db=self.db).get_by_user_id(user_id)
        if result is None:
            raise EventServiceException("no user with such tg_id found")
        if not UserRoles.TEACHER in result.payload.roles:
            raise EventServiceException("incorrect role. please contact with administrator")

        # get
        res = await PeopleRepository(db=self.db).get_by_user_id(user_id=user_id)
        if res is None:
            raise EventServiceException("no user with such mail found")
        return res.payload

    # TODO: implement
    async def _extend_event(self, event: EventModel,
                            session: AsyncIOMotorClientSession | None = None) -> ExtendedEventModel:
        res = await EventBankingAccountsRepository(db=self.db).get_account_by_event_id(event_id=event.eventId,
                                                                                       session=session)
        # get event banking account info
        if res is None:
            raise EventServiceException("event banking account error")
        return ExtendedEventModel(**event.model_dump(), init_balance=res.payload.init_balance,
                                  balance=res.payload.balance, bankAccountId=res.payload.accountId)

    async def get_all_hosted_events(self, user_id: int) -> List[ExtendedEventModel]:
        person = await self._get_user_from_tg_id(user_id)
        raw_events = await EventService(db=self.db).get_all_events_by_email(email=person.email)
        events = [await self._extend_event(event) for event in raw_events]
        return events

    # TODO: maybe check permission here
    async def get_one_hosted_event(self, user_id: int, event_id: str,
                                   session: AsyncIOMotorClientSession | None = None) -> ExtendedEventModel:
        """
        get info about one concrete event by id, if user is allowed to get this info
        """
        person = await self._get_user_from_tg_id(user_id)
        raw_event = await EventService(db=self.db).get_event_by_id(event_id=event_id, session=session)
        if person.email not in raw_event.speakers:
            raise EventServiceException(
                "access denied: you are not allowed to get event extended info if you are not speaker")
        event = await self._extend_event(raw_event, session=session)
        return event

    # TODO: type check
    async def get_event_participants(self, event_id: str, session: AsyncIOMotorClientSession | None = None):
        raw_event = await EventService(db=self.db).get_event_by_id(event_id=event_id, session=session)
        res = await ParticipantsService(db=self.db).get_event_participants(event=raw_event, session=session)
        return res

    # TODO: type check
    async def send_token_to_participant(self, user_id: int, event_id: str, receiver_id: int, amount: int) -> \
    SimpleResult[EventToUserPaymentDB]:
        """
        Процесс проведения перевода:
        1. проверяем существование мероприятия и аккаунта мероприятия eventBankingAccountId
        2. проверяем существование отправителя и права отправителя
        3. проверяем существование получателя и его участие в мероприятии, userbankingaccount
        4. проверка на переводы в процессе?????
        5. создаем event to user payment обязательство (проверки?)
        6. пушим create event to user payment
            Тут уже делается в бд-левел ПРОВЕРИТЬ ЧТО:
                Порядок создания нового money transfer (возможно это делает скорее сервис, но и на уровне бд
                будем пытаться поддерживать на всякий):
                1. проверяем, есть ли активные money transfer операции у этого пользователя/аккаунта.
                   Если есть, то отклоняем (пытаемся поддерживать инвариант: в один момент времени
                   только одна операция покупки)
                3. возможно еще проверяем штуку "не начисляй одному и тому же, если полминуты не прошло"
        7. money transfer session с event to user payment
        8. меняем статус event to user payment в соответствие с результатом money transfer
           (возможно внутри money transfer)
        """
        async with await self.db.client.start_session() as session:
            try:
                async with session.start_transaction():
                    # step 1 event checking
                    # step 2 sender checking
                    ext_event = await self.get_one_hosted_event(user_id=user_id, event_id=event_id, session=session)
                    # step 3 receiver checking
                    participants = await self.get_event_participants(event_id=event_id, session=session)
                    receiver = None
                    for participant in participants:
                        if participant.tg_id == receiver_id:
                            receiver = participant
                    if receiver is None:
                        raise EventServiceException("receiver not found in event participants")
                    receiver_account_res = await UserBankingAccountsRepository(db=self.db).get_account_by_user_id(
                        user_id=receiver_id, session=session)
                    if isinstance(receiver_account_res, SimpleErrorResult):
                        raise Exception("receiver account getting error")
                    receiver_account = receiver_account_res.payload
                    # step 5 event to user payment object
                    payment = EventToUserPaymentDB(
                        fromEventBankingAccount=ext_event.bankAccountId,
                        toUserBankingAccount=receiver_account.accountId,
                        amount=amount,
                    )
                    # step 6 event to user payment push
                    res = await EventToUserPaymentsRepository(db=self.db).create_payment(payment=payment,
                                                                                         session=session)
                    if isinstance(res, SimpleErrorResult):
                        raise Exception("payment creating error")
                    payment = res.payload
                    # step 7 money transfer
                    await MoneyTransferService(db=self.db).event_to_user_transfer_money(session=session,
                                                                                        from_acc=payment.fromEventBankingAccount,
                                                                                        to_acc=payment.toUserBankingAccount,
                                                                                        amount=payment.amount,
                                                                                        operation_id=str(
                                                                                            payment.id), )
                    # step 8 result pushing
                    inner_res = await EventToUserPaymentsRepository(db=self.db).change_payment_status(
                        payment_id=payment.payment_id,
                        status=TransferStatus.completed, session=session)
            except Exception as e:
                return SimpleErrorResult(message=str("Transaction failed: " + str(e)))

            return SimpleOkResult(payload=inner_res.payload)
