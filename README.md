# Syllabase

Syllabase is a course-aware AI assistant with:

- A `FastAPI` backend (`backend/`) for course, syllabus, and chat APIs.
- A `React + Vite` frontend (`frontend/`) for selecting context and chatting.

## Project Structure

- `backend/`: FastAPI app, routers, schemas, services, Supabase integration.
- `frontend/`: React UI, API client, chat and selection components.

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm 9+

## Backend Setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
BACKEND_CORS_ORIGIN_REGEX=
```

For deployments where frontend URLs vary (for example Render preview/static domains), you can set:

```env
BACKEND_CORS_ORIGIN_REGEX=https://.*\.onrender\.com
```

Run backend:

```powershell
uvicorn main:app --reload
```

Backend default URL: `http://127.0.0.1:8000`

## Uptime Monitoring (UptimeRobot)

- Health endpoint: `GET/HEAD /health`
- Monitor URL example: `https://syllabase.onrender.com/health`
- Recommended monitor type: `HTTP(s)` with `HEAD` request method
- Expected success: HTTP `200`

## Backend API

Main route groups (browse interactively at `http://127.0.0.1:8000/docs` while the backend is running):

- `programmes`: CRUD for academic programmes.
- `courses`: CRUD for courses and course lookup by programme/code.
- `units`: Unit management and bulk syllabus insertion.
- `topics`: Topic CRUD and bulk topic insertion per unit.
- `references`: Course reference CRUD and bulk reference insertion.
- `syllabus`: Consolidated syllabus fetch by course.
- `mcp`: Context selection, course-grounded prompt validation, and chat response flow.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

## Development Notes

- Backend CORS is controlled by `BACKEND_CORS_ORIGINS` and optional `BACKEND_CORS_ORIGIN_REGEX` in `backend/.env`.
- Backend app title is `Syllabase API`.
- If Windows venv launcher paths break after moving folders, reinstall the package in that venv (for example: `python -m pip install --force-reinstall uvicorn`).

## Scripts

Frontend (`frontend/package.json`):

- `npm run dev`: Start Vite dev server.
- `npm run build`: Build production bundle.
- `npm run lint`: Run ESLint.
- `npm run preview`: Preview built app.
