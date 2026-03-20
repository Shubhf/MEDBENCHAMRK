"""GitHub repository extractor for medical AI codebases."""

from __future__ import annotations

import re
from typing import Any

import httpx

from backend.extractors.base import BaseExtractor, MedicalDocument, Chunk


def _parse_repo(url: str) -> tuple[str, str]:
    m = re.search(r"github\.com/([^/]+)/([^/?\s#]+)", url)
    if m:
        return m.group(1), m.group(2).rstrip(".git")
    raise ValueError(f"Cannot parse GitHub repo from: {url}")


class GitHubExtractor(BaseExtractor):
    """Extract key information from a GitHub medical AI repository."""

    async def extract(self, source: str, **kwargs: Any) -> MedicalDocument:
        owner, repo = _parse_repo(source)

        async with httpx.AsyncClient(timeout=30.0) as http:
            # Repo metadata
            meta_resp = await http.get(f"https://api.github.com/repos/{owner}/{repo}")
            meta = meta_resp.json() if meta_resp.status_code == 200 else {}

            # README
            readme_text = ""
            for readme_path in ["README.md", "readme.md", "README.rst"]:
                r = await http.get(
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/{readme_path}"
                )
                if r.status_code == 200:
                    readme_text = r.text
                    break
                r = await http.get(
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/{readme_path}"
                )
                if r.status_code == 200:
                    readme_text = r.text
                    break

            # requirements.txt
            reqs = ""
            for reqs_path in ["requirements.txt", "setup.py", "pyproject.toml"]:
                r = await http.get(
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/{reqs_path}"
                )
                if r.status_code == 200:
                    reqs = r.text[:5000]
                    break

        title = meta.get("description", "") or f"{owner}/{repo}"
        stars = meta.get("stargazers_count", 0)
        topics = meta.get("topics", [])

        combined = f"# {owner}/{repo}\n\n{title}\n\nStars: {stars}\nTopics: {', '.join(topics)}\n\n"
        combined += f"## README\n{readme_text[:20000]}\n\n"
        if reqs:
            combined += f"## Dependencies\n{reqs}\n"

        chunks: list[Chunk] = []
        words = combined.split()
        for i in range(0, len(words), 500):
            chunk_text = " ".join(words[i : i + 500])
            chunks.append(Chunk(text=chunk_text, section="Repository", chunk_index=len(chunks)))

        return MedicalDocument(
            source_type="github",
            source_url=source,
            title=f"{owner}/{repo}: {title}",
            raw_content=combined,
            content_chunks=chunks,
            metadata={
                "owner": owner,
                "repo": repo,
                "stars": stars,
                "topics": topics,
                "has_requirements": bool(reqs),
            },
        )
