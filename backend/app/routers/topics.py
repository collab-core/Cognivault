from fastapi import APIRouter

from app.db.supabase_client import supabase
from app.schemas.syllabus import TopicBatchCreate
from app.schemas.updates import TopicUpdate

router = APIRouter(tags=["topics"])


@router.post("/topics/bulk")
def create_topics_bulk(payload: TopicBatchCreate):
    rows = [{"unit_id": payload.unit_id, "topic_name": t.topic_name} for t in payload.topics]

    if not rows:
        return {"message": "No topics to insert", "count": 0, "data": []}

    result = supabase.table("topics").insert(rows).execute()
    return {"message": "Topics inserted successfully", "count": len(rows), "data": result.data}


@router.post("/topics")
def create_topic(unit_id: str, topic_name: str):
    result = supabase.table("topics").insert({"unit_id": unit_id, "topic_name": topic_name}).execute()
    return result.data


@router.patch("/topics/{topic_id}")
def update_topic(topic_id: str, payload: TopicUpdate):
    result = supabase.table("topics").update({"topic_name": payload.topic_name}).eq("id", topic_id).execute()
    return result.data


@router.get("/units/{unit_id}/topics")
def get_topics(unit_id: str):
    result = supabase.table("topics").select("*").eq("unit_id", unit_id).execute()
    return result.data


@router.delete("/topics/{topic_id}")
def delete_topic(topic_id: str):
    supabase.table("topics").delete().eq("id", topic_id).execute()
    return {"message": "Topic deleted"}
