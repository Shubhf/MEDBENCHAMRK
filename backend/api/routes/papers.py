"""Paper/source management routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel

from backend.db import supabase as db
from backend.api.deps import get_current_user, get_llm_router
from backend.processors.universal import MedicalAIInputProcessor

router = APIRouter()


class URLRequest(BaseModel):
    url: str


class BatchURLRequest(BaseModel):
    urls: list[str]


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Upload a PDF paper (up to 100MB)."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")

    # Save to Supabase storage
    file_path = f"{user['id']}/{uuid.uuid4()}.pdf"
    storage_url = db.upload_file("medical-papers", file_path, content)

    # Save temp file for processing
    import tempfile, os

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        processor = MedicalAIInputProcessor(llm_router=get_llm_router())
        doc = await processor.process(tmp_path, user["id"], is_file=True)
        doc.source_url = storage_url
        db.update("sources", doc.id, {"source_url": storage_url, "local_filename": file.filename})
        return {"id": doc.id, "title": doc.title, "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        os.unlink(tmp_path)


@router.post("/url")
async def submit_url(
    req: URLRequest,
    user: dict = Depends(get_current_user),
):
    """Submit a URL (ArXiv, PubMed, YouTube, GitHub, etc.)."""
    try:
        processor = MedicalAIInputProcessor(llm_router=get_llm_router())
        doc = await processor.process(req.url, user["id"])
        return {"id": doc.id, "title": doc.title, "source_type": doc.source_type, "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/batch")
async def submit_batch(
    req: BatchURLRequest,
    user: dict = Depends(get_current_user),
):
    """Submit multiple URLs at once."""
    results = []
    processor = MedicalAIInputProcessor(llm_router=get_llm_router())
    for url in req.urls[:50]:  # Max 50 at once
        try:
            doc = await processor.process(url, user["id"])
            results.append({"url": url, "id": doc.id, "title": doc.title, "status": "completed"})
        except Exception as e:
            results.append({"url": url, "status": "failed", "error": str(e)})
    return {"results": results}


@router.get("/")
async def list_papers(
    user: dict = Depends(get_current_user),
    modality: str | None = None,
    anatomy: str | None = None,
    limit: int = 50,
):
    """List user's papers with optional filters."""
    sources = db.select("sources", filters={"user_id": user["id"]}, order="-created_at", limit=limit, service=True)
    if modality:
        sources = [s for s in sources if modality in (s.get("imaging_modalities") or [])]
    if anatomy:
        sources = [s for s in sources if anatomy in (s.get("anatomies") or [])]
    return {"papers": sources, "total": len(sources)}


@router.get("/{paper_id}")
async def get_paper(paper_id: str, user: dict = Depends(get_current_user)):
    results = db.select("sources", filters={"id": paper_id, "user_id": user["id"]}, service=True)
    if not results:
        raise HTTPException(status_code=404, detail="Paper not found")
    return results[0]


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str, user: dict = Depends(get_current_user)):
    db.delete("sources", paper_id, service=True)
    return {"success": True}


@router.get("/{paper_id}/chunks")
async def get_chunks(paper_id: str, user: dict = Depends(get_current_user)):
    chunks = db.select("chunks", filters={"source_id": paper_id, "user_id": user["id"]}, service=True)
    return {"chunks": chunks}
