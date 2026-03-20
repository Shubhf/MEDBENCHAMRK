"""YouTube extractor — conference talk transcripts (no API key needed)."""

from __future__ import annotations

import re
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi
import httpx

from backend.extractors.base import BaseExtractor, MedicalDocument, Chunk


def _parse_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"embed/([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError(f"Cannot parse YouTube video ID from: {url}")


class YouTubeExtractor(BaseExtractor):
    """Extract transcript from YouTube videos (conference talks, lectures)."""

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        video_id = _parse_video_id(source)

        # Fetch title from oEmbed (no API key needed)
        title = await self._fetch_title(video_id)

        # Fetch transcript
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception:
            # Try auto-generated captions
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=["en"]
                )
            except Exception as e:
                raise ValueError(f"No transcript available for video {video_id}: {e}")

        # Build full text with timestamps
        full_text = ""
        for entry in transcript_list:
            full_text += entry["text"] + " "
        full_text = full_text.strip()

        # Chunk transcript into ~500-word segments
        chunks = self._chunk_transcript(transcript_list)

        return MedicalDocument(
            source_type="youtube",
            source_url=source,
            title=title,
            raw_content=full_text,
            content_chunks=chunks,
            metadata={"video_id": video_id},
        )

    async def _fetch_title(self, video_id: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10.0) as http:
                r = await http.get(
                    f"https://www.youtube.com/oembed?url=https://youtube.com/watch?v={video_id}&format=json"
                )
                if r.status_code == 200:
                    return r.json().get("title", "")
        except Exception:
            pass
        return f"YouTube Video {video_id}"

    def _chunk_transcript(
        self, transcript: list[dict], words_per_chunk: int = 500
    ) -> list[Chunk]:
        chunks: list[Chunk] = []
        current_words: list[str] = []
        current_start = 0.0
        idx = 0

        for entry in transcript:
            words = entry["text"].split()
            if not current_words:
                current_start = entry["start"]
            current_words.extend(words)

            if len(current_words) >= words_per_chunk:
                text = " ".join(current_words)
                minutes = int(current_start // 60)
                seconds = int(current_start % 60)
                chunks.append(
                    Chunk(
                        text=text,
                        section=f"Timestamp {minutes:02d}:{seconds:02d}",
                        chunk_index=idx,
                    )
                )
                idx += 1
                current_words = []

        if current_words:
            text = " ".join(current_words)
            minutes = int(current_start // 60)
            seconds = int(current_start % 60)
            chunks.append(
                Chunk(
                    text=text,
                    section=f"Timestamp {minutes:02d}:{seconds:02d}",
                    chunk_index=idx,
                )
            )

        return chunks
