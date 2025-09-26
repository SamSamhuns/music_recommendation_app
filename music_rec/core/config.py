"""
Load configurations and constants 
"""
import os
from logging.config import dictConfig
from models.logging import LogConfig
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv(override=True)

# project information
PROJECT_NAME: str = "Music Analysis API template"
PROJECT_DESCRIPTION: str = "Template API for Music Analysis"
DEBUG: bool = os.environ.get("DEBUG", "") != "False"
VERSION: str = "0.0.1"

# server settings
FASTAPI_SERVER_PORT = int(os.getenv("FASTAPI_SERVER_PORT", default="8080"))

# save directories
ROOT_STORAGE_DIR = os.getenv("ROOT_STORAGE_DIR", default="volumes/music_analysis")
FILE_STORAGE_DIR = os.getenv("FILE_STORAGE_DIR", default=os.path.join(ROOT_STORAGE_DIR, "files"))
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", default=os.path.join(ROOT_STORAGE_DIR, "vector_store"))
LOG_STORAGE_DIR = os.getenv("LOG_STORAGE_DIR", default=os.path.join(ROOT_STORAGE_DIR, "logs"))

os.makedirs(ROOT_STORAGE_DIR, exist_ok=True)
os.makedirs(FILE_STORAGE_DIR, exist_ok=True)
os.makedirs(LOG_STORAGE_DIR, exist_ok=True)

# logging conf
log_cfg = LogConfig()
# override info & error log paths
log_cfg.handlers["info_rotating_file_handler"]["filename"] = os.path.join(LOG_STORAGE_DIR, "info.log")
log_cfg.handlers["warning_file_handler"]["filename"] = os.path.join(LOG_STORAGE_DIR, "error.log")
log_cfg.handlers["error_file_handler"]["filename"] = os.path.join(LOG_STORAGE_DIR, "error.log")
dictConfig(log_cfg.model_dump())

# mysql conf
POSTGRES_HOST = os.getenv("POSTRES_HOST", default="0.0.0.0")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", default="5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", default="user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", default="pass")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", default="default")

# Spotify API conf
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
