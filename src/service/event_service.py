from typing import List

from ..database.models import PyObjectId
from models.event import EventModel
from ..database.repositories.competitions_repository import CompetitionsRepository
from ..database.repositories.courses_repository import CoursesRepository
from ..database.repositories.open_lectures_repository import OpenLecturesRepository
from ..database.repositories.school_repository import SchoolsRepository


class EventService:
    def __init__(self, db):
        self.db = db
        self.opelLecturesRepository = OpenLecturesRepository(self.db)
        self.coursesRepository = CoursesRepository(self.db)
        self.schoolsRepository = SchoolsRepository(self.db)
        self.competitionsRepository = CompetitionsRepository(self.db)

    async def get_all_events(self) -> List[EventModel]:
        events : List[EventModel] = list()
        open_lectures = await self.opelLecturesRepository.find_by(query={})
        for lecture in open_lectures:
            events.append(EventModel.from_open_lecture(lecture))
        competitions = await self.competitionsRepository.find_by(query={})
        for competition in competitions:
            events.append(EventModel.from_competition(competition))
        courses = await self.coursesRepository.find_by(query={})
        for course in courses:
            events.append(EventModel.from_course(course))
        schools = await self.schoolsRepository.find_by(query={})
        for school in schools:
            events.append(EventModel.from_school(school))
        return events