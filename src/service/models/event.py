from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict

from ...database.models import PyObjectId, OpenLectureDB, CourseDB, CompetitionDB, SchoolDB

DATE_FORMAT="%-d.%m.%Y"
weekday_abbr_ru = {
    0: 'ПН',
    1: 'ВТ',
    2: 'СР',
    3: 'ЧТ',
    4: 'ПТ',
    5: 'СБ',
    6: 'ВС'
}
season_rus = {
    "autumn": "Осень",
    "spring": "Весна",
}

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
    dateTags: Optional[List[str]] = None
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
            if not date_value.strip():
                return None
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

    #  #todo: fix shittycode about datetags

    @classmethod
    def from_open_lecture(cls, lecture: OpenLectureDB) -> "EventModel":
        date_tags: List[str] = list()
        if lecture.date:
            date_tags.append(lecture.date.strftime(DATE_FORMAT) + ", " + weekday_abbr_ru[lecture.date.weekday()]) #todo: fix shittycode
        if lecture.time:
            date_tags.append(lecture.time)
        return cls(
            _id=lecture.id,
            eventId=lecture.openLectureId,
            title=lecture.title,
            type=EventType.open_lecture,
            shortDescription=lecture.shortDescription,
            tags=lecture.tags,
            dateTags=date_tags if date_tags else None,
            speakers=lecture.speakers if lecture.speakers else list(),
            registrationLink=lecture.registrationLink,
            created_at=lecture.created_at,
            updated_at=lecture.updated_at,
        )

    @classmethod
    def from_course(cls, course: CourseDB) -> "EventModel":
        date_tags: List[str] = list()
        if course.season and course.year:
            date_tags.append(season_rus[course.season] + ' ' + course.year)
        return cls(
            _id=course.id,
            eventId=course.courseId,
            title=course.title,
            type=EventType.course,
            shortDescription=course.shortDescription,
            tags=course.tags,
            dateTags=date_tags if date_tags else None,
            speakers=course.speakers if course.speakers else list(),
            registrationLink=course.registrationLink,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )

    @classmethod
    def from_competition(cls, competition: CompetitionDB) -> "EventModel":
        date_tags: List[str] = list()
        if competition.dateStart and competition.dateEnd:
            date_tags.append(competition.dateStart.strftime(DATE_FORMAT) + " - " + competition.dateEnd.strftime(DATE_FORMAT))
        elif competition.dateStart:
            date_tags.append(competition.dateStart.strftime(DATE_FORMAT))
        elif competition.dateEnd:
            date_tags.append(competition.dateEnd.strftime(DATE_FORMAT))
        return cls(
            _id=competition.id,
            eventId=competition.competitionId,
            title=competition.title,
            type=EventType.competition,
            shortDescription=competition.shortDescription,
            tags=competition.tags,
            dateTags=date_tags if date_tags else None,
            registrationDeadline=competition.registrationDeadline,
            registrationLink=competition.registrationLink,
            speakers=competition.speakers if competition.speakers else list(),
            created_at=competition.created_at,
            updated_at=competition.updated_at,
        )
    @classmethod
    def from_school(cls, school: SchoolDB) -> "EventModel":
        date_tags: List[str] = list()
        if school.dateStart and school.dateEnd:
            date_tags.append(school.dateStart.strftime(DATE_FORMAT) + " - " + school.dateEnd.strftime(DATE_FORMAT))
        elif school.dateStart:
            date_tags.append(school.dateStart.strftime(DATE_FORMAT))
        elif school.dateEnd:
            date_tags.append(school.dateEnd.strftime(DATE_FORMAT))
        return cls(
            _id=school.id,
            eventId=school.openLectureId,
            title=school.title,
            type=EventType.school,
            shortDescription=school.shortDescription,
            tags=school.tags,
            dateTags=date_tags if date_tags else None,
            speakers=school.speakers if school.speakers else list(),
            registrationDeadline=school.registrationDeadline,
            registrationLink=school.registrationLink,
            created_at=school.created_at,
            updated_at=school.updated_at,
        )