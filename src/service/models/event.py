import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

from ...database.models import PyObjectId, OpenLectureDB, CourseDB, CompetitionDB, SchoolDB


class EventType(str, Enum):
    course = "course"
    open_lecture = "open_lecture"
    competition = "competition"
    school = "school"

class EventModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    eventId: str
    title: str
    type: EventType
    shortDescription: str
    tags: Optional[List[str]] = None
    registrationLink: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_open_lecture(cls, lecture: OpenLectureDB) -> "EventModel":
        return cls(
            _id=lecture.id,
            eventId=lecture.openLectureId,
            title=lecture.title,
            type=EventType.open_lecture,
            shortDescription=lecture.shortDescription,
            tags=lecture.tags,
            registrationLink=lecture.registrationLink,
            created_at=lecture.created_at,
            updated_at=lecture.updated_at,
        )

    @classmethod
    def from_course(cls, course: CourseDB) -> "EventModel":
        return cls(
            _id=course.id,
            eventId=course.courseId,
            title=course.title,
            type=EventType.course,
            shortDescription=course.shortDescription,
            tags=course.tags,
            registrationLink=course.registrationLink,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )

    @classmethod
    def from_competition(cls, competition: CompetitionDB) -> "EventModel":
        return cls(
            _id=competition.id,
            eventId=competition.competitionId,
            title=competition.title,
            type=EventType.competition,
            shortDescription=competition.shortDescription,
            tags=competition.tags,
            registrationLink=competition.registrationLink,
            created_at=competition.created_at,
            updated_at=competition.updated_at,
        )
    @classmethod
    def from_school(cls, school: SchoolDB) -> "EventModel":
        return cls(
            _id=school.id,
            eventId=school.openLectureId,
            title=school.title,
            type=EventType.school,
            shortDescription=school.shortDescription,
            tags=school.tags,
            registrationLink=school.registrationLink,
            created_at=school.created_at,
            updated_at=school.updated_at,
        )