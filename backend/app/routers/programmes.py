from typing import Any, Dict, List

from fastapi import APIRouter, Body

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.creates import ProgrammeCreate
from app.schemas.responses import MessageResponse
from app.schemas.updates import ProgrammeUpdate

router = APIRouter(tags=["programmes"])


@router.post("/programmes", response_model=List[Dict[str, Any]])
def create_programme(
    payload: ProgrammeCreate = Body(
        ...,
        examples={
            "default": {
                "summary": "Create programme",
                "value": {"code": "CSE", "name": "Computer Science and Engineering"},
            }
        },
    )
):
    result = supabase.table("programmes").insert(payload.model_dump()).execute()
    return result.data


@router.patch("/programmes/{programme_id}")
def update_programme(programme_id: str, payload: ProgrammeUpdate):
    update_data = non_null_update_data(payload)
    result = supabase.table("programmes").update(update_data).eq("id", programme_id).execute()
    return result.data


@router.get("/programmes")
def get_programmes():
    result = supabase.table("programmes").select("*").execute()
    return result.data


@router.delete("/programmes/{programme_id}", response_model=MessageResponse)
def delete_programme(programme_id: str):
    supabase.table("programmes").delete().eq("id", programme_id).execute()
    return {"message": "Programme deleted"}
