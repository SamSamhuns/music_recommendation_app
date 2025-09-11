"""
Upsert file api
"""
import logging

from fastapi import APIRouter

# from api.mysql import entries_exist, insert_data_into_sql, insert_bulk_data_into_sql


SUPPORTED_FILES_EXT = {".txt", ".pdf", ".html", ".json"}
router = APIRouter()
logger = logging.getLogger('upsert_route')

