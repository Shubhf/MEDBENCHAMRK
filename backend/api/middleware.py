"""Middleware for request logging, error handling, and training data capture."""

from __future__ import annotations

import time
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start
        log.info(
            "%s %s %d %.2fs",
            request.method, request.url.path, response.status_code, duration,
        )
        return response
