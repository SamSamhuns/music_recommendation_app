"""
Upsert file api
"""

import logging

from fastapi import APIRouter


SUPPORTED_FILES_EXT = {".txt", ".pdf", ".html", ".json"}
router = APIRouter()
logger = logging.getLogger("upsert_route")
