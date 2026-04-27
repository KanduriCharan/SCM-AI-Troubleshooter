from fastapi import FastAPI
from app.api.routes import router as analyze_router
from app.core.config import settings
from app.api.upload_routes import router as upload_router
from app.api.risk_routes import router as risk_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Enterprise-style SCM AI Troubleshooter",
)
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8000",
    "https://scm-ai-troubleshooter-2h3zwebrxpguyddekhddgm.streamlit.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(upload_router)
app.include_router(risk_router)