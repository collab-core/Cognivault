from typing import Optional

from pydantic import BaseModel


class ProgrammeUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    semester: Optional[int] = None
    course_number: Optional[int] = None


class UnitUpdate(BaseModel):
    title: Optional[str] = None
    marks_weight: Optional[int] = None


class TopicUpdate(BaseModel):
    topic_name: str


class ReferenceUpdate(BaseModel):
    citation: Optional[str] = None
    ref_type: Optional[str] = None
