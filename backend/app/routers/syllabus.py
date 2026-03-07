from fastapi import APIRouter, HTTPException

from app.db.supabase_client import supabase

router = APIRouter(tags=["syllabus"])


@router.get("/courses/{course_id}/syllabus")
def get_full_syllabus(course_id: str):
    try:
        result = (
            supabase.table("units")
            .select("unit_number,title,marks_weight,topics(*)")
            .eq("course_id", course_id)
            .order("unit_number")
            .execute()
        )
        return result.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
