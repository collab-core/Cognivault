import os

from dotenv import load_dotenv

load_dotenv()


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return ["http://localhost:5173", "http://localhost:3000"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
BACKEND_CORS_ORIGINS = _parse_cors_origins(os.getenv("BACKEND_CORS_ORIGINS"))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
    )
