from typing import Any, Dict, List

from fastapi import APIRouter, Body

from app.db.supabase_client import supabase
from app.schemas.creates import TopicCreateRequest
from app.schemas.responses import BulkTopicsResponse, MessageResponse
from app.schemas.syllabus import TopicBatchCreate
from app.schemas.updates import TopicUpdate

router = APIRouter(tags=["topics"])


@router.post("/topics/bulk", response_model=BulkTopicsResponse)
def create_topics_bulk(
    payload: TopicBatchCreate = Body(
        ...,
        examples={
            "default": {
                "summary": "Create topics in bulk",
                "value": {
                    "unit_id": "u1a2b3c4-0000-1111-2222-333344445555",
                    "topics": [{"topic_name": "Stacks"}, {"topic_name": "Queues"}],
                },
            }
        },
    )
):
    rows = [{"unit_id": payload.unit_id, "topic_name": t.topic_name} for t in payload.topics]

    if not rows:
        return {"message": "No topics to insert", "count": 0, "data": []}

    result = supabase.table("topics").insert(rows).execute()
    return {"message": "Topics inserted successfully", "count": len(rows), "data": result.data}


@router.post("/topics", response_model=List[Dict[str, Any]])
def create_topic(
    payload: TopicCreateRequest = Body(
        ...,
        examples={
            "default": {
                "summary": "Create topic",
                "value": {
                    "unit_id": "u1a2b3c4-0000-1111-2222-333344445555",
                    "topic_name": "Linked Lists",
                },
            }
        },
    )
):
    result = supabase.table("topics").insert(payload.model_dump()).execute()
    return result.data


@router.patch("/topics/{topic_id}")
def update_topic(topic_id: str, payload: TopicUpdate):
    result = supabase.table("topics").update({"topic_name": payload.topic_name}).eq("id", topic_id).execute()
    return result.data


@router.get("/units/{unit_id}/topics")
def get_topics(unit_id: str):
    result = supabase.table("topics").select("*").eq("unit_id", unit_id).execute()
    return result.data


@router.delete("/topics/{topic_id}", response_model=MessageResponse)
def delete_topic(topic_id: str):
    supabase.table("topics").delete().eq("id", topic_id).execute()
    return {"message": "Topic deleted"}
