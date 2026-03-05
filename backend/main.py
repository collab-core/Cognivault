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


# ----------------------
# Upload Endpoint
# ----------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()

    # Unique file path
    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    # Upload to PRIVATE bucket
    supabase.storage.from_("materials").upload(
        unique_filename,
        contents,
        {"content-type": "application/pdf"}
    )

    # Store metadata in DB
    result = supabase.table("materials").insert({
        "title": file.filename,
        "subject": "General",
        "file_path": unique_filename
    }).execute()

    return {
        "message": "Uploaded successfully",
        "material_id": result.data[0]["id"]
    }


# ----------------------
# Generate Signed URL
# ----------------------
@app.get("/materials/{material_id}/download")
def get_signed_url(material_id: str):

    # Get file path from DB
    result = supabase.table("materials").select("*").eq("id", material_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Material not found")

    file_path = result.data[0]["file_path"]

    # Create signed URL (valid for 1 hour)
    signed_url = supabase.storage.from_("materials").create_signed_url(
        file_path,
        expires_in=3600
    )

    return {
        "signed_url": signed_url["signedURL"]
    }

@app.delete("/materials/{material_id}")
def delete_material(material_id: str):

    # Get file path from DB
    result = supabase.table("materials").select("*").eq("id", material_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Material not found")

    file_path = result.data[0]["file_path"]

    # Delete from storage
    supabase.storage.from_("materials").remove([file_path])

    # Delete from DB
    supabase.table("materials").delete().eq("id", material_id).execute()

    return {"message": "Material deleted successfully"}

@app.get("/materials")
def list_materials():
    result = supabase.table("materials") \
        .select("id, title, subject, created_at") \
        .order("created_at", desc=True) \
        .execute()

    return result.data