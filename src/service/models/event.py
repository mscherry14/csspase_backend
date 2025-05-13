from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict

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
    speakers: List[EmailStr] = Field(default=list)
    tags: Optional[List[str]] = None
    registrationDeadline: Optional[datetime] = None
    registrationLink: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_date(cls, values):
        date_value = values.get("date")
        if isinstance(date_value, dict) and "$date" in date_value:
            date_value = date_value["$date"]
        if isinstance(date_value, str):
            values["date"] = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return values

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    """
        1. Save speakers if they are in DB and refactor to model without
           unnecessary information (??? maybe to person schema!)
        2. Save time to tags if time correctly provided
        3. If there are registration deadline set the registrationDeadline
    """

    # TODO: implement comment

    @classmethod
    def from_open_lecture(cls, lecture: OpenLectureDB) -> "EventModel":
        return cls(
            _id=lecture.id,
            eventId=lecture.openLectureId,
            title=lecture.title,
            type=EventType.open_lecture,
            shortDescription=lecture.shortDescription,
            tags=lecture.tags,
            speakers=lecture.speakers if lecture.speakers else list(),
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
            speakers=course.speakers if course.speakers else list(),
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
            speakers=competition.speakers if competition.speakers else list(),
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
            speakers=school.speakers if school.speakers else list(),
            registrationLink=school.registrationLink,
            created_at=school.created_at,
            updated_at=school.updated_at,
        )