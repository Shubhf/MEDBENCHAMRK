"""Medical Q&A Agent — zero hallucination, citation-grounded answers."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from backend.db import supabase as db
from backend.llm.router import LLMRouter
from backend.processors.embedder import Embedder

log = logging.getLogger(__name__)


@dataclass
class Citation:
    paper_title: str = ""
    section: str = ""
    page: int | None = None
    quote: str = ""
    source_id: str = ""


@dataclass
class QAResponse:
    answer: str = ""
    citations: list[Citation] = field(default_factory=list)
    confidence: float = 0.0
    query: str = ""


class MedicalQAAgent:
    """Grounded Q&A over medical AI papers. Every answer must cite sources."""

    def __init__(self, llm: LLMRouter | None = None) -> None:
        self.llm = llm or LLMRouter()
        self.embedder = Embedder()

    async def ask(
        self, query: str, user_id: str, source_ids: list[str] | None = None
    ) -> QAResponse:
        """Answer a question grounded in the user's papers."""
        # Retrieve relevant chunks
        query_embedding = await self.embedder.embed(query)
        chunks = db.vector_search(
            query_embedding, user_id, source_ids=source_ids, top_k=15
        )

        if not chunks:
            return QAResponse(
                answer="Not found in your papers. Please upload relevant medical AI papers first.",
                confidence=0.0,
                query=query,
            )

        # Build context from chunks
        context = self._build_context(chunks)

        # Get source titles for citation
        source_titles: dict[str, str] = {}
        for c in chunks:
            sid = c.get("source_id", "")
            if sid and sid not in source_titles:
                sources = db.select("sources", filters={"id": sid}, columns="title", service=True)
                if sources:
                    source_titles[sid] = sources[0].get("title", "Unknown")

        prompt = f"""Answer this medical AI research question using ONLY the provided paper excerpts.

Question: {query}

Paper Excerpts:
{context}

RULES:
1. ONLY use information from the excerpts above
2. For every claim, cite the specific paper and section
3. If the information is not in the excerpts, say "Not found in your papers"
4. Never fabricate clinical claims, statistics, or paper titles
5. Include a confidence score (0.0-1.0) based on how well the excerpts answer the question
6. Be specific — include exact numbers, dataset names, and metric values when available

Return valid JSON:
{{
  "answer": "Your detailed answer with inline citations",
  "citations": [
    {{"paper_title": "...", "section": "...", "page": null, "quote": "exact text from excerpt"}}
  ],
  "confidence": 0.0
}}"""

        try:
            response = await self.llm.generate(
                "qa_grounded", prompt,
                system_prompt="You are a medical AI research assistant. Answer ONLY from provided sources. Never hallucinate.",
                json_mode=True, temperature=0.1,
            )
            data = json.loads(response)

            citations = []
            for c in data.get("citations", []):
                citations.append(Citation(
                    paper_title=c.get("paper_title", ""),
                    section=c.get("section", ""),
                    page=c.get("page"),
                    quote=c.get("quote", ""),
                ))

            return QAResponse(
                answer=data.get("answer", ""),
                citations=citations,
                confidence=float(data.get("confidence", 0.0)),
                query=query,
            )
        except Exception as e:
            log.error("QA LLM call failed: %s", e)
            return QAResponse(
                answer=f"Error processing your question: {str(e)}",
                confidence=0.0,
                query=query,
            )

    async def ask_stream(
        self, query: str, user_id: str, source_ids: list[str] | None = None
    ) -> AsyncIterator[str]:
        """Stream answer tokens for SSE responses."""
        query_embedding = await self.embedder.embed(query)
        chunks = db.vector_search(query_embedding, user_id, source_ids=source_ids, top_k=15)

        if not chunks:
            yield "Not found in your papers. Please upload relevant medical AI papers first."
            return

        context = self._build_context(chunks)

        prompt = f"""Answer this medical AI research question using ONLY the provided paper excerpts.
Cite specific papers for every claim. If not found, say so.

Question: {query}

Paper Excerpts:
{context}"""

        async for token in self.llm.generate_stream(
            "qa_grounded", prompt,
            system_prompt="You are a medical AI research assistant. Answer ONLY from provided sources. Cite paper titles.",
            temperature=0.1,
        ):
            yield token

    def _build_context(self, chunks: list[dict]) -> str:
        parts = []
        for i, c in enumerate(chunks):
            section = c.get("section_name", "")
            page = c.get("page_number", "")
            source_id = c.get("source_id", "")
            sim = c.get("similarity", 0)
            content = c.get("content", "")
            parts.append(
                f"[Excerpt {i+1}] Source: {source_id} | Section: {section} | Page: {page} | Relevance: {sim:.2f}\n{content}"
            )
        return "\n\n".join(parts)
