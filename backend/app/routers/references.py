from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException

from app.db.supabase_client import supabase
from app.routers._utils import non_null_update_data
from app.schemas.creates import ReferenceCreate
from app.schemas.responses import BulkReferencesResponse, MessageResponse
from app.schemas.syllabus import ReferenceBatchCreate
from app.schemas.updates import ReferenceUpdate

router = APIRouter(tags=["references"])


@router.post("/references/bulk", response_model=BulkReferencesResponse)
def add_references_bulk(
    payload: ReferenceBatchCreate = Body(
        ...,
        examples={
            "default": {
                "summary": "Add references in bulk",
                "value": {
                    "course_id": "a1b2c3d4-0000-1111-2222-333344445555",
                    "references": [
                        {
                            "ref_type": "textbook",
                            "citation": "Cormen, Leiserson, Rivest, Stein - Introduction to Algorithms",
                        },
                        {
                            "ref_type": "reference",
                            "citation": "Knuth - The Art of Computer Programming",
                        },
                    ],
                },
            }
        },
    )
):
    rows = [
        {"course_id": payload.course_id, "ref_type": ref.ref_type, "citation": ref.citation}
        for ref in payload.references
    ]

    if not rows:
        return {"message": "No references to insert", "count": 0, "data": []}

    try:
        result = supabase.table("course_references").insert(rows).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"message": "References inserted successfully", "count": len(rows), "data": result.data}


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
    result = supabase.table("course_references").insert(payload.model_dump()).execute()
    return result.data


@router.patch("/references/{reference_id}")
def update_reference(reference_id: str, payload: ReferenceUpdate):
    update_data = non_null_update_data(payload)
    result = supabase.table("course_references").update(update_data).eq("id", reference_id).execute()
    return result.data


@router.get("/courses/{course_id}/references")
def get_references(course_id: str):
    result = supabase.table("course_references").select("*").eq("course_id", course_id).execute()
    return result.data


@router.delete("/references/{reference_id}", response_model=MessageResponse)
def delete_reference(reference_id: str):
    supabase.table("course_references").delete().eq("id", reference_id).execute()
    return {"message": "Reference deleted"}
