from fastapi import APIRouter

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.syllabus import SyllabusCreate
from app.schemas.updates import UnitUpdate

router = APIRouter(tags=["units"])


@router.post("/syllabus/bulk")
def create_syllabus_bulk(payload: SyllabusCreate):
    inserted_units = []

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

    return {
        "message": "Syllabus inserted successfully",
        "units_processed": len(inserted_units),
        "details": inserted_units,
    }


@router.post("/units")
def create_unit(course_id: str, unit_number: int, title: str, marks_weight: int):
    result = supabase.table("units").insert(
        {
            "course_id": course_id,
            "unit_number": unit_number,
            "title": title,
            "marks_weight": marks_weight,
        }
    ).execute()
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


@router.delete("/units/{unit_id}")
def delete_unit(unit_id: str):
    supabase.table("units").delete().eq("id", unit_id).execute()
    return {"message": "Unit deleted"}
