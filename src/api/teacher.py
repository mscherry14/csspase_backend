from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.api.auth import get_current_user_tg_id, teacher_role_checker
from src.api.schemas.event_full_schema import EventFullSchema
from src.api.schemas.event_short_schema import EventShortSchema
from src.api.schemas.event_to_user_money_transfer_schema import EventToUserMoneyTransferSchema
from src.api.schemas.event_to_user_payment_request_schema import EventToUserPaymentRequestSchema
from src.api.schemas.participant_schema import ParticipantSchema
from src.database.database import db
from src.database.models import UserRoles
from src.database.repositories.users_repository import UsersRepository
from src.service.teacher_event_service import TeacherEventService
from src.utils.simple_result import SimpleErrorResult, SimpleOkResult

# from app.schemas import EventShort, EventFull, ParticipantDetail
# from app.services import AuthService

ROLE = UserRoles.TEACHER
router = APIRouter(prefix="/teacher", dependencies=[Depends(teacher_role_checker)])


@router.get("/events", response_model=List[EventShortSchema])
async def get_events(tg_id: int = Depends(get_current_user_tg_id)):
    """Список событий, доступных учителю."""
    try:
        res = await TeacherEventService(db=db).get_all_hosted_events(user_id=tg_id)
        return list(map(EventShortSchema.from_extended_event, res))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}", response_model=EventFullSchema)
async def get_event(event_id: str, tg_id: int = Depends(get_current_user_tg_id)):
    """Подробности события без участников."""
    try:
        res = await TeacherEventService(db=db).get_one_hosted_event(event_id=event_id, user_id=tg_id)
        return await EventFullSchema.from_extended_event(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#
# #????
@router.get("/events/{event_id}/participants", response_model=List[ParticipantSchema])
async def get_participant(event_id: str, tg_id: int = Depends(get_current_user_tg_id)):
    """Список участников события."""
    try:
        res = await TeacherEventService(db=db).get_event_participants(event_id=event_id, user_id=tg_id)
        return [await ParticipantSchema.from_user_db(x, event_id) for x in res]
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

#maybe /events/{event_id}/accrue,
@router.post("/events/{event_id}/participants/{participant_id}", response_model=EventToUserMoneyTransferSchema)
async def reward_participant(event_id: str, participant_id: int, req_body: EventToUserPaymentRequestSchema, tg_id: int = Depends(get_current_user_tg_id)):
    """Начислить баллы участнику."""
    try:
        res = await TeacherEventService(db=db).send_token_to_participant(user_id=tg_id, event_id=event_id, amount=req_body.amount, receiver_id=participant_id)
        if isinstance(res, SimpleErrorResult):
            raise HTTPException(status_code=404, detail=res.message)
        participant = await UsersRepository(db=db).get_by_user_id(user_id=participant_id)
        name = ""
        if isinstance(participant, SimpleOkResult):
            name = participant.payload.name #так всегда должно быть, если предыдущая операция успешна
        return EventToUserMoneyTransferSchema(receiverName=name, amount=res.payload.amount, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# @router.get("/events/{event_id}/participants/{participant_id}", response_model=ParticipantDetail)
# async def get_participant(event_id: str, participant_id: str, tg_id: int = Depends(get_current_user_tg_id)):
#     """Данные участника события."""
#     return {"user_id": participant_id, "reward": 10.0, "awarded_by": tg_id}
