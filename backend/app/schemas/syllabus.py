from typing import Dict, List, Optional

from pydantic import BaseModel


class UnitCreate(BaseModel):
    unit_number: int
    title: str
    marks_weight: Optional[int] = None
    topics: List[str]


class SyllabusCreate(BaseModel):
    course_id: str
    units: List[UnitCreate]


class TopicCreate(BaseModel):
    topic_name: str


class TopicBatchCreate(BaseModel):
    unit_id: str
    topics: List[TopicCreate]


class ReferenceItem(BaseModel):
    ref_type: str
    citation: str


class ReferenceBatchCreate(BaseModel):
    course_id: str
    references: List[ReferenceItem]
