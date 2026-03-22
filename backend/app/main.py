from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import BACKEND_CORS_ORIGINS
from app.routers.courses import router as courses_router
from app.routers.mcp import router as mcp_router
from app.routers.programmes import router as programmes_router
from app.routers.references import router as references_router
from app.routers.syllabus import router as syllabus_router
from app.routers.topics import router as topics_router
from app.routers.units import router as units_router

app = FastAPI(title="Syllabase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(programmes_router)
app.include_router(courses_router)
app.include_router(units_router)
app.include_router(topics_router)
app.include_router(references_router)
app.include_router(syllabus_router)
app.include_router(mcp_router)
