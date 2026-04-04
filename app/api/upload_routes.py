from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.RAG.document_ingestor import ingest_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    uploads_dir = Path(settings.uploads_directory)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    save_path = uploads_dir / file.filename

    content = await file.read()
    save_path.write_bytes(content)

    result = ingest_pdf(str(save_path))
    return result