from typing import Any, Dict, List

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class BulkSyllabusUnitDetail(BaseModel):
    unit_id: str
    title: str
    topics_inserted: int


class BulkSyllabusResponse(BaseModel):
    message: str
    units_processed: int
    details: List[BulkSyllabusUnitDetail]


class BulkTopicsResponse(BaseModel):
    message: str
    count: int
    data: List[Dict[str, Any]]