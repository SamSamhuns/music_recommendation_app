"""
SQL Question Answer api endpoint
"""

import logging

from fastapi import APIRouter


router = APIRouter()
logger = logging.getLogger("sql_qa_route")
