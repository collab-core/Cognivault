from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.creates import UnitCreateRequest
from app.schemas.responses import BulkSyllabusResponse, MessageResponse
from app.schemas.syllabus import SyllabusCreate
from app.schemas.updates import UnitUpdate

router = APIRouter(tags=["units"])


@router.post("/syllabus/bulk", response_model=BulkSyllabusResponse)
def create_syllabus_bulk(
    payload: SyllabusCreate = Body(
        ...,
        examples={
            "default": {
                "summary": "Create syllabus in bulk",
                "value": {
                    "course_id": "a1b2c3d4-0000-1111-2222-333344445555",
                    "units": [
                        {
                            "unit_number": 1,
                            "title": "Introduction",
                            "marks_weight": 10,
                            "topics": ["Overview", "History"],
                        }
                    ],
                },
            }
        },
    )
):
    inserted_units = []
    inserted_unit_ids = []

    try:
        for unit in payload.units:
            unit_result = supabase.table("units").insert(
                {
                    "course_id": payload.course_id,
                    "unit_number": unit.unit_number,
                    "title": unit.title,
                    "marks_weight": unit.marks_weight,
                }
            ).execute()

            unit_id = unit_result.data[0]["id"]
            inserted_unit_ids.append(unit_id)

            topic_rows = [{"unit_id": unit_id, "topic_name": topic} for topic in unit.topics]

            if topic_rows:
                supabase.table("topics").insert(topic_rows).execute()

            inserted_units.append(
                {
                    "unit_id": unit_id,
                    "title": unit.title,
                    "topics_inserted": len(topic_rows),
                }
            )
    except Exception as exc:
        if inserted_unit_ids:
            supabase.table("topics").delete().in_("unit_id", inserted_unit_ids).execute()
            supabase.table("units").delete().in_("id", inserted_unit_ids).execute()
        raise HTTPException(
            status_code=500,
            detail="Bulk syllabus insert failed and was rolled back",
        ) from exc

    return {
        "message": "Syllabus inserted successfully",
        "units_processed": len(inserted_units),
        "details": inserted_units,
    }


@router.post("/units", response_model=List[Dict[str, Any]])
def create_unit(
    payload: UnitCreateRequest = Body(
        ...,
        examples={
            "default": {
                "summary": "Create unit",
                "value": {
                    "course_id": "a1b2c3d4-0000-1111-2222-333344445555",
                    "unit_number": 2,
                    "title": "Data Structures",
                    "marks_weight": 20,
                },
            }
        },
    )
):
    result = supabase.table("units").insert(payload.model_dump()).execute()
    return result.data


@router.patch("/units/{unit_id}")
def update_unit(unit_id: str, payload: UnitUpdate):
    update_data = non_null_update_data(payload)
    result = supabase.table("units").update(update_data).eq("id", unit_id).execute()
    return result.data


@router.get("/courses/{course_id}/units")
def get_units(course_id: str):
    result = (
        supabase.table("units")
        .select("*")
        .eq("course_id", course_id)
        .order("unit_number")
        .execute()
    )
    return result.data


@router.delete("/units/{unit_id}", response_model=MessageResponse)
def delete_unit(unit_id: str):
    supabase.table("units").delete().eq("id", unit_id).execute()
    return {"message": "Unit deleted"}
