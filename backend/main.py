from fastapi import FastAPI, UploadFile, File, HTTPException
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


#Programmes
@app.post("/programmes")
def create_programme(code: str, name: str):
    result = supabase.table("programmes").insert({
        "code": code,
        "name": name
    }).execute()

    return result.data

@app.get("/programmes")
def get_programmes():
    result = supabase.table("programmes").select("*").execute()
    return result.data


#Courses
@app.post("/courses")
def create_course(
    code: str,
    name: str,
    regulation_year: int,
    programme_id: str,
    semester: int,
    course_number: int
):
    result = supabase.table("courses").insert({
        "code": code,
        "name": name,
        "regulation_year": regulation_year,
        "programme_id": programme_id,
        "semester": semester,
        "course_number": course_number
    }).execute()

    return result.data

@app.get("/courses/programme/{programme_id}")
def get_courses_by_programme(programme_id: str):

    result = supabase.table("courses") \
        .select("*") \
        .eq("programme_id", programme_id) \
        .execute()

    return result.data

@app.get("/courses/{course_code}")
def get_course(course_code: str):

    result = supabase.table("courses") \
        .select("*") \
        .eq("code", course_code) \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Course not found")

    return result.data[0]

#Units
@app.post("/units")
def create_unit(
    course_id: str,
    unit_number: int,
    title: str,
    marks_weight: int
):
    result = supabase.table("units").insert({
        "course_id": course_id,
        "unit_number": unit_number,
        "title": title,
        "marks_weight": marks_weight
    }).execute()

    return result.data

@app.get("/courses/{course_id}/units")
def get_units(course_id: str):

    result = supabase.table("units") \
        .select("*") \
        .eq("course_id", course_id) \
        .order("unit_number") \
        .execute()

    return result.data

#Topics
@app.post("/topics")
def create_topic(unit_id: str, topic_name: str):

    result = supabase.table("topics").insert({
        "unit_id": unit_id,
        "topic_name": topic_name
    }).execute()

    return result.data

@app.get("/units/{unit_id}/topics")
def get_topics(unit_id: str):

    result = supabase.table("topics") \
        .select("*") \
        .eq("unit_id", unit_id) \
        .execute()

    return result.data

#References
@app.post("/references")
def add_reference(course_id: str, ref_type: str, citation: str):

    result = supabase.table("references").insert({
        "course_id": course_id,
        "ref_type": ref_type,
        "citation": citation
    }).execute()

    return result.data

@app.get("/courses/{course_id}/references")
def get_references(course_id: str):

    result = supabase.table("references") \
        .select("*") \
        .eq("course_id", course_id) \
        .execute()

    return result.data

#Get full syllabus for a course
@app.get("/courses/{course_id}/syllabus")
def get_full_syllabus(course_id: str):

    units = supabase.table("units") \
        .select("*") \
        .eq("course_id", course_id) \
        .order("unit_number") \
        .execute()

    syllabus = []

    for unit in units.data:
        topics = supabase.table("topics") \
            .select("*") \
            .eq("unit_id", unit["id"]) \
            .execute()

        syllabus.append({
            "unit_number": unit["unit_number"],
            "title": unit["title"],
            "marks_weight": unit["marks_weight"],
            "topics": topics.data
        })

    return syllabus