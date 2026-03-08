from time import time
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, HTTPException

from app.db.supabase_client import supabase
from app.schemas.mcp import McpChatResponse, McpCourseOption, McpGroundRequest, McpGroundResponse
from app.services.llm_chat import generate_answer
from app.services.llm_relevance import classify_prompt_relevance

router = APIRouter(prefix="/mcp", tags=["mcp"])

_COURSE_CONTEXT_CACHE_TTL_SECONDS = 300
_COURSE_CONTEXT_CACHE: Dict[str, Tuple[float, List[str], List[str]]] = {}


def _get_course_context_lines(course_id: str) -> Tuple[List[str], List[str]]:
    cached = _COURSE_CONTEXT_CACHE.get(course_id)
    if cached and (time() - cached[0]) <= _COURSE_CONTEXT_CACHE_TTL_SECONDS:
        return cached[1], cached[2]

    units_result = (
        supabase.table("units")
        .select("unit_number,title,marks_weight,topics(topic_name)")
        .eq("course_id", course_id)
        .order("unit_number")
        .execute()
    )

    refs_result = (
        supabase.table("course_references")
        .select("ref_type,citation")
        .eq("course_id", course_id)
        .execute()
    )

    units_text = []
    for unit in units_result.data:
        topic_names = [topic["topic_name"] for topic in unit.get("topics", [])]
        units_text.append(
            f"Unit {unit['unit_number']}: {unit['title']} (marks_weight={unit.get('marks_weight')})\\n"
            f"Topics: {', '.join(topic_names) if topic_names else 'None'}"
        )

    refs_text = [f"- [{ref['ref_type']}] {ref['citation']}" for ref in refs_result.data]
    _COURSE_CONTEXT_CACHE[course_id] = (time(), units_text, refs_text)
    return units_text, refs_text


@router.get("/selections")
def get_selection_values() -> Dict[str, List[Any]]:
    programmes = supabase.table("programmes").select("id,code,name").order("name").execute()
    courses = supabase.table("courses").select("semester,regulation_year").execute()

    semesters = sorted({row["semester"] for row in courses.data if row.get("semester") is not None})
    regulation_years = sorted(
        {row["regulation_year"] for row in courses.data if row.get("regulation_year") is not None}
    )

    return {
        "programmes": programmes.data,
        "semesters": semesters,
        "regulation_years": regulation_years,
    }


@router.get("/courses", response_model=List[McpCourseOption])
def get_courses_for_selection(programme_id: str, semester: int, regulation_year: int):
    result = (
        supabase.table("courses")
        .select("id,code,name,semester,regulation_year")
        .eq("programme_id", programme_id)
        .eq("semester", semester)
        .eq("regulation_year", regulation_year)
        .order("course_number")
        .execute()
    )
    return result.data


@router.post("/ground", response_model=McpGroundResponse)
def ground_prompt(payload: McpGroundRequest):
    try:
        course_result = (
            supabase.table("courses")
            .select("id,code,name,programme_id,semester,regulation_year")
            .eq("id", payload.course_id)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load course: {exc}") from exc

    if not course_result.data:
        raise HTTPException(status_code=404, detail="Course not found")

    course = course_result.data[0]

    if (
        course["programme_id"] != payload.selection.programme_id
        or course["semester"] != payload.selection.semester
        or course["regulation_year"] != payload.selection.regulation_year
    ):
        raise HTTPException(
            status_code=400,
            detail="Selected course does not match programme/semester/regulation selection",
        )

    try:
        units_text, refs_text = _get_course_context_lines(course["id"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load syllabus context: {exc}") from exc

    relevance_syllabus_context = (
        f"Course: {course['name']} ({course['code']})\\n"
        f"Syllabus Units:\\n{chr(10).join(units_text) if units_text else 'No units available.'}"
    )

    try:
        relevant, reason = classify_prompt_relevance(
            course_name=course["name"],
            course_code=course["code"],
            user_prompt=payload.user_prompt,
            syllabus_context=relevance_syllabus_context,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Relevance check failed: {exc}") from exc

    if not relevant:
        return {
            "course_id": course["id"],
            "course_code": course["code"],
            "relevant": False,
            "reason": reason,
            "augmented_prompt": None,
        }

    syllabus_context = (
        f"Course: {course['name']} ({course['code']})\\n"
        f"Programme ID: {course['programme_id']}\\n"
        f"Semester: {course['semester']}\\n"
        f"Regulation Year: {course['regulation_year']}\\n\\n"
        f"Syllabus Units:\\n{chr(10).join(units_text) if units_text else 'No units available.'}\\n\\n"
        f"References:\\n{chr(10).join(refs_text) if refs_text else 'No references available.'}"
    )

    augmented_prompt = (
        "You must answer only using the syllabus context below. "
        "If information is missing from context, say you do not have enough syllabus information.\\n\\n"
        f"[SYLLABUS CONTEXT START]\\n{syllabus_context}\\n[SYLLABUS CONTEXT END]\\n\\n"
        f"[USER PROMPT]\\n{payload.user_prompt}"
    )

    return {
        "course_id": course["id"],
        "course_code": course["code"],
        "relevant": True,
        "reason": reason,
        "augmented_prompt": augmented_prompt,
    }


@router.post("/chat", response_model=McpChatResponse)
def chat_with_context(payload: McpGroundRequest):
    """Ground the prompt against the syllabus and return an LLM-generated answer."""
    ground_result = ground_prompt(payload)

    if not ground_result["relevant"]:
        return {
            "course_id": ground_result["course_id"],
            "course_code": ground_result["course_code"],
            "relevant": False,
            "reason": ground_result["reason"],
            "answer": None,
        }

    try:
        answer = generate_answer(ground_result["augmented_prompt"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {exc}") from exc

    return {
        "course_id": ground_result["course_id"],
        "course_code": ground_result["course_code"],
        "relevant": True,
        "reason": ground_result["reason"],
        "answer": answer,
    }
