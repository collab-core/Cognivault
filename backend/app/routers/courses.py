from fastapi import APIRouter, HTTPException

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.updates import CourseUpdate

router = APIRouter(tags=["courses"])


@router.post("/courses")
def create_course(
    code: str,
    name: str,
    regulation_year: int,
    programme_id: str,
    semester: int,
    course_number: int,
):
    result = supabase.table("courses").insert(
        {
            "code": code,
            "name": name,
            "regulation_year": regulation_year,
            "programme_id": programme_id,
            "semester": semester,
            "course_number": course_number,
        }
    ).execute()
    return result.data


@router.patch("/courses/{course_id}")
def update_course(course_id: str, payload: CourseUpdate):
    update_data = non_null_update_data(payload)
    result = supabase.table("courses").update(update_data).eq("id", course_id).execute()
    return result.data


@router.get("/courses/programme/{programme_id}")
def get_courses_by_programme(programme_id: str):
    result = supabase.table("courses").select("*").eq("programme_id", programme_id).execute()
    return result.data


@router.get("/courses/{course_code}")
def get_course(course_code: str):
    result = supabase.table("courses").select("*").eq("code", course_code).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Course not found")
    return result.data[0]


@router.delete("/courses/{course_id}")
def delete_course(course_id: str):
    supabase.table("courses").delete().eq("id", course_id).execute()
    return {"message": "Course deleted"}
