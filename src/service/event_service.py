from typing import List

from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import EmailStr

from models.event import EventModel
from ..database.repositories.competitions_repository import CompetitionsRepository
from ..database.repositories.courses_repository import CoursesRepository
from ..database.repositories.open_lectures_repository import OpenLecturesRepository
from ..database.repositories.school_repository import SchoolsRepository
from ..utils.simple_result import SimpleErrorResult, SimpleOkResult


class EventServiceException(Exception):
    pass

class EventService:
    def __init__(self, db):
        self.db = db
        self.opelLecturesRepository = OpenLecturesRepository(self.db)
        self.coursesRepository = CoursesRepository(self.db)
        self.schoolsRepository = SchoolsRepository(self.db)
        self.competitionsRepository = CompetitionsRepository(self.db)

    async def get_all_events(self, session: AsyncIOMotorClientSession | None = None) -> List[EventModel]:
        events : List[EventModel] = list()
        res = await self.opelLecturesRepository.find_all(session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: open lectures: " + res.message)
        for lecture in res.payload:
            events.append(EventModel.from_open_lecture(lecture))

        res = await self.competitionsRepository.find_all(session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: competitions: " + res.message)
        for competition in res.payload:
            events.append(EventModel.from_competition(competition))

        res = await self.coursesRepository.find_all(session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: courses: " + res.message)
        for course in res.payload:
            events.append(EventModel.from_course(course))

        res = await self.schoolsRepository.find_all(session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: schools: " + res.message)
        for school in res.payload:
            events.append(EventModel.from_school(school))
        return events

    async def get_all_events_by_email(self, email: EmailStr, session: AsyncIOMotorClientSession | None = None) -> List[EventModel]:
        events : List[EventModel] = list()
        res = await self.opelLecturesRepository.find_all_with_speaker(speaker=email, session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: open lectures: " + res.message)
        for lecture in res.payload:
            events.append(EventModel.from_open_lecture(lecture))

        res = await self.competitionsRepository.find_all_with_speaker(speaker=email, session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: competitions: " + res.message)
        for competition in res.payload:
            events.append(EventModel.from_competition(competition))

        res = await self.coursesRepository.find_all_with_speaker(speaker=email, session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: courses: " + res.message)
        for course in res.payload:
            events.append(EventModel.from_course(course))

        res = await self.schoolsRepository.find_all_with_speaker(speaker=email, session=session)
        if isinstance(res, SimpleErrorResult):
            raise EventServiceException("Data getting error: schools: " + res.message)
        for school in res.payload:
            events.append(EventModel.from_school(school))
        return events

    async def get_event_by_id(self, event_id: str, session: AsyncIOMotorClientSession | None = None) -> EventModel:
        res = await self.opelLecturesRepository.find_by_event_id(event_id=event_id, session=session)
        if isinstance(res, SimpleOkResult):
            return EventModel.from_open_lecture(res.payload)

        res = await self.competitionsRepository.find_by_event_id(event_id=event_id, session=session)
        if isinstance(res, SimpleOkResult):
            return EventModel.from_competition(res.payload)

        res = await self.coursesRepository.find_by_event_id(event_id=event_id, session=session)
        if isinstance(res, SimpleOkResult):
            return EventModel.from_course(res.payload)

        res = await self.schoolsRepository.find_by_event_id(event_id=event_id, session=session)
        if isinstance(res, SimpleOkResult):
            return EventModel.from_school(res.payload)

        raise EventServiceException("Data getting error: no event found")