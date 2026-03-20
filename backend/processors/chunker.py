"""Text chunker with sentence boundary respect and section awareness."""

from __future__ import annotations

import re

from backend.extractors.base import Chunk


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    page: int | None = None,
    section: str | None = None,
) -> list[Chunk]:
    """Split text into chunks respecting sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[Chunk] = []
    current: list[str] = []
    current_len = 0
    idx = 0

    for sent in sentences:
        word_count = len(sent.split())
        if current_len + word_count > chunk_size and current:
            chunk_text_str = " ".join(current)
            chunks.append(Chunk(text=chunk_text_str, page=page, section=section, chunk_index=idx))
            idx += 1
            # Keep overlap
            overlap_words: list[str] = []
            overlap_count = 0
            for s in reversed(current):
                wc = len(s.split())
                if overlap_count + wc > overlap:
                    break
                overlap_words.insert(0, s)
                overlap_count += wc
            current = overlap_words
            current_len = overlap_count

        current.append(sent)
        current_len += word_count

    if current:
        chunks.append(Chunk(text=" ".join(current), page=page, section=section, chunk_index=idx))

    return chunks
