"""Celery background tasks for document processing."""

from __future__ import annotations

import os
import logging

from celery import Celery

log = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("medresearch", broker=REDIS_URL, backend=REDIS_URL)
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
)


@app.task(bind=True, max_retries=3)
def process_source(self, source_url: str, user_id: str, is_file: bool = False):
    """Main background processing pipeline for a source."""
    import asyncio
    from backend.processors.universal import MedicalAIInputProcessor
    from backend.llm.router import LLMRouter
    from backend.processors.graph_builder import KnowledgeGraphBuilder

    async def _run():
        processor = MedicalAIInputProcessor(llm_router=LLMRouter())
        doc = await processor.process(source_url, user_id, is_file=is_file)

        # Build knowledge graph
        graph_builder = KnowledgeGraphBuilder()
        await graph_builder.build_from_document(doc, user_id)

        return doc.id

    try:
        return asyncio.run(_run())
    except Exception as exc:
        log.error("Processing failed for %s: %s", source_url, exc)
        self.retry(exc=exc, countdown=30)
