from pydantic import BaseModel


class ProgrammeCreate(BaseModel):
    code: str
    name: str


class CourseCreate(BaseModel):
    code: str
    name: str
    regulation_year: int
    programme_id: str
    semester: int
    course_number: int


class UnitCreateRequest(BaseModel):
    course_id: str
    unit_number: int
    title: str
    marks_weight: int


class TopicCreateRequest(BaseModel):
    unit_id: str
    topic_name: str


class ReferenceCreate(BaseModel):
    course_id: str
    ref_type: str
    citation: str