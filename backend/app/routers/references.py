from typing import Any, Dict, List

from fastapi import APIRouter, Body

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.creates import ReferenceCreate
from app.schemas.responses import MessageResponse
from app.schemas.updates import ReferenceUpdate

router = APIRouter(tags=["references"])


@router.post("/references", response_model=List[Dict[str, Any]])
def add_reference(
    payload: ReferenceCreate = Body(
        ...,
        examples={
            "default": {
                "summary": "Add reference",
                "value": {
                    "course_id": "a1b2c3d4-0000-1111-2222-333344445555",
                    "ref_type": "textbook",
                    "citation": "Aho, Hopcroft, Ullman - Data Structures and Algorithms",
                },
            }
        },
    )
):
    result = supabase.table("references").insert(payload.model_dump()).execute()
    return result.data


@router.patch("/references/{reference_id}")
def update_reference(reference_id: str, payload: ReferenceUpdate):
    update_data = non_null_update_data(payload)
    result = supabase.table("references").update(update_data).eq("id", reference_id).execute()
    return result.data


@router.get("/courses/{course_id}/references")
def get_references(course_id: str):
    result = supabase.table("references").select("*").eq("course_id", course_id).execute()
    return result.data


@router.delete("/references/{reference_id}", response_model=MessageResponse)
def delete_reference(reference_id: str):
    supabase.table("references").delete().eq("id", reference_id).execute()
    return {"message": "Reference deleted"}
