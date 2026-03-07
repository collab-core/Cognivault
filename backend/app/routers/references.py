from fastapi import APIRouter

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.updates import ReferenceUpdate

router = APIRouter(tags=["references"])


@router.post("/references")
def add_reference(course_id: str, ref_type: str, citation: str):
    result = supabase.table("references").insert(
        {"course_id": course_id, "ref_type": ref_type, "citation": citation}
    ).execute()
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


@router.delete("/references/{reference_id}")
def delete_reference(reference_id: str):
    supabase.table("references").delete().eq("id", reference_id).execute()
    return {"message": "Reference deleted"}
