"""MedResearch Mind — FastAPI Application."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import auth, papers, gaps, qa, compare, experiment, memory, benchmark

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(
    title="MedResearch Mind",
    description="The Research Brain for Medical AI",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://medresearchmind.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(gaps.router, prefix="/api/gaps", tags=["gaps"])
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])
app.include_router(compare.router, prefix="/api/compare", tags=["compare"])
app.include_router(experiment.router, prefix="/api/experiment", tags=["experiment"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(benchmark.router, prefix="/api/benchmark", tags=["benchmark"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0"}


@app.post("/api/waitlist")
async def join_waitlist(data: dict):
    """Public endpoint — no auth required."""
    from backend.db import supabase as db

    try:
        db.insert("waitlist", {
            "email": data.get("email", ""),
            "full_name": data.get("full_name", ""),
            "institution": data.get("institution", ""),
            "clinical_role": data.get("clinical_role", ""),
            "research_area": data.get("research_area", ""),
        })
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.on_event("startup")
async def startup():
    log.info("MedResearch Mind starting up...")
    hf_token = os.getenv("HF_TOKEN", "")
    if hf_token:
        log.info("HuggingFace embeddings configured (production mode)")
    else:
        # Check Ollama for local dev
        from backend.llm.ollama import OllamaLLM
        ollama = OllamaLLM()
        if await ollama.health():
            log.info("Ollama is running (local embeddings)")
        else:
            log.warning("No embedding provider — set HF_TOKEN or run: ollama pull nomic-embed-text")
        await ollama.close()


# Serve frontend static files in production
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "out")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
