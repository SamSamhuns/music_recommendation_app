"""
SQL Question Answer api endpoint
"""
import logging
from fastapi import APIRouter

# from api.langchain_custom.text2sql import text_to_sql

router = APIRouter()
logger = logging.getLogger('sql_qa_route')
