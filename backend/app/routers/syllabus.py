from fastapi import APIRouter

from app.db.supabase_client import supabase

router = APIRouter(tags=["syllabus"])


@router.get("/courses/{course_id}/syllabus")
def get_full_syllabus(course_id: str):
    units = (
        supabase.table("units")
        .select("*")
        .eq("course_id", course_id)
        .order("unit_number")
        .execute()
    )

    syllabus = []

    for unit in units.data:
        topics = supabase.table("topics").select("*").eq("unit_id", unit["id"]).execute()
        syllabus.append(
            {
                "unit_number": unit["unit_number"],
                "title": unit["title"],
                "marks_weight": unit["marks_weight"],
                "topics": topics.data,
            }
        )

    return syllabus
