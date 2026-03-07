from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.creates import CourseCreate
from app.schemas.responses import MessageResponse
from app.schemas.updates import CourseUpdate

router = APIRouter(tags=["courses"])


@router.post("/courses", response_model=List[Dict[str, Any]])
def create_course(
    payload: CourseCreate = Body(
        ...,
        examples={
            "default": {
                "summary": "Create course",
                "value": {
                    "code": "CS101",
                    "name": "Programming Fundamentals",
                    "regulation_year": 2024,
                    "programme_id": "a1b2c3d4-0000-1111-2222-333344445555",
                    "semester": 1,
                    "course_number": 1,
                },
            }
        },
    )
):
    result = supabase.table("courses").insert(payload.model_dump()).execute()
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


@router.delete("/courses/{course_id}", response_model=MessageResponse)
def delete_course(course_id: str):
    supabase.table("courses").delete().eq("id", course_id).execute()
    return {"message": "Course deleted"}
