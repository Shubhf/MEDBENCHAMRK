"""Supabase client wrapper for MedResearch Mind."""

from __future__ import annotations

import os
import hashlib
from typing import Any

from supabase import create_client, Client


def _get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing environment variable: {key}")
    return val


_client: Client | None = None
_service_client: Client | None = None


def get_client() -> Client:
    """Return the anon-key Supabase client (RLS enforced)."""
    global _client
    if _client is None:
        _client = create_client(_get_env("SUPABASE_URL"), _get_env("SUPABASE_ANON_KEY"))
    return _client


def get_service_client() -> Client:
    """Return the service-role client (bypasses RLS). Use for training_data, etc."""
    global _service_client
    if _service_client is None:
        _service_client = create_client(
            _get_env("SUPABASE_URL"), _get_env("SUPABASE_SERVICE_KEY")
        )
    return _service_client


# ── Helpers ─────────────────────────────────────────────────


def insert(table: str, data: dict[str, Any], *, service: bool = False) -> dict:
    """Insert a row and return the inserted record."""
    client = get_service_client() if service else get_client()
    resp = client.table(table).insert(data).execute()
    return resp.data[0] if resp.data else {}


def select(
    table: str,
    *,
    columns: str = "*",
    filters: dict[str, Any] | None = None,
    order: str | None = None,
    limit: int | None = None,
    service: bool = False,
) -> list[dict]:
    """Flexible SELECT helper."""
    client = get_service_client() if service else get_client()
    q = client.table(table).select(columns)
    if filters:
        for col, val in filters.items():
            q = q.eq(col, val)
    if order:
        desc = order.startswith("-")
        q = q.order(order.lstrip("-"), desc=desc)
    if limit:
        q = q.limit(limit)
    resp = q.execute()
    return resp.data or []


def update(
    table: str, row_id: str, data: dict[str, Any], *, service: bool = False
) -> dict:
    client = get_service_client() if service else get_client()
    resp = client.table(table).update(data).eq("id", row_id).execute()
    return resp.data[0] if resp.data else {}


def delete(table: str, row_id: str, *, service: bool = False) -> None:
    client = get_service_client() if service else get_client()
    client.table(table).delete().eq("id", row_id).execute()


def rpc(fn_name: str, params: dict[str, Any], *, service: bool = False) -> Any:
    """Call a Supabase RPC function (e.g. match_chunks)."""
    client = get_service_client() if service else get_client()
    resp = client.rpc(fn_name, params).execute()
    return resp.data


def vector_search(
    query_embedding: list[float],
    user_id: str,
    *,
    source_ids: list[str] | None = None,
    top_k: int = 10,
) -> list[dict]:
    """Semantic similarity search via the match_chunks RPC."""
    params: dict[str, Any] = {
        "query_embedding": query_embedding,
        "match_count": top_k,
        "filter_user_id": user_id,
    }
    if source_ids:
        params["filter_source_ids"] = source_ids
    return rpc("match_chunks", params, service=True)


# ── Storage helpers ─────────────────────────────────────────


def upload_file(bucket: str, path: str, file_bytes: bytes, content_type: str = "application/pdf") -> str:
    """Upload a file to Supabase Storage and return its public URL."""
    client = get_service_client()
    client.storage.from_(bucket).upload(path, file_bytes, {"content-type": content_type})
    return client.storage.from_(bucket).get_public_url(path)


def download_file(bucket: str, path: str) -> bytes:
    client = get_service_client()
    return client.storage.from_(bucket).download(path)


def anonymize_user_id(user_id: str) -> str:
    """One-way hash for training data — never store real user IDs."""
    return hashlib.sha256(f"medresearch-{user_id}".encode()).hexdigest()[:16]
