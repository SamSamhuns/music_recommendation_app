"""
Main fastapi server file

This file contains the main FastAPI server setup. It:
- Creates the FastAPI music_rec
- Adds middleware (CORS, timing)
- Mounts static files
- Includes API routers
- Defines an OpenAPI schema
- Starts a Uvicorn server

Args:
    cfg (module): Configuration variables
    upsert (module): Upsert API router
    sql (module): SQL qa API router

Returns:
    music_rec (FastAPI): The FastAPI application object
"""
import os
import time
import argparse
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import core.config as cfg
from routes import upsert, sql


def get_application():
    """Returns a FastAPI music_rec object.  

    Returns:
        music_rec (FastAPI): A FastAPI music_rec object.
    """
    music_rec = FastAPI(title=cfg.PROJECT_NAME,
                  description=cfg.PROJECT_DESCRIPTION,
                  debug=cfg.DEBUG,
                  version=cfg.VERSION)
    music_rec.mount("/static", StaticFiles(directory="./music_rec/static"), name="static")
    music_rec.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return music_rec


# Docs
def custom_openapi():
    """Returns the OpenAPI schema for the FastAPI music_rec.

    Returns:
        openapi_schema (dict): The OpenAPI schema.
    """
    if music_rec.openapi_schema:
        return music_rec.openapi_schema
    openapi_schema = get_openapi(
        title=cfg.PROJECT_NAME,
        version=cfg.VERSION,
        description=cfg.PROJECT_DESCRIPTION,
        routes=music_rec.routes,
    )
    music_rec.openapi_schema = openapi_schema
    return music_rec.openapi_schema


# logging
logger = logging.getLogger("music_analysis_server")

# Routing
music_rec = get_application()
music_rec.include_router(upsert.router, prefix="/upsert", tags=["upsert"])
music_rec.include_router(sql.router, prefix="/sql", tags=["sql"])
music_rec.openapi = custom_openapi


# api call time middleware
@music_rec.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Adds an X-Process-Time header with the time taken to process the request.

    Args:
        request (Request): The request object.
        call_next (coroutine): The next middleware or endpoint.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@music_rec.get("/")
async def index():
    """Returns a welcome message."""
    return {"Welcome to the Log Analysis service": "Please visit /docs for list of apis"}


@music_rec.get('/favicon.ico')
async def favicon():
    """Returns the favicon.ico file."""
    file_name = "favicon.ico"
    file_path = os.path.join(music_rec.root_path, "music_rec/static", file_name)
    return FileResponse(path=file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        """Start FastAPI with uvicorn server hosting log analyzer""")
    parser.add_argument('--ip', '--host_ip', dest="host_ip", type=str, default="0.0.0.0",
                        help='host ip address. (default: %(default)s)')
    parser.add_argument('-p', '--port', type=int, default=cfg.FASTAPI_SERVER_PORT,
                        help='uvicorn port number. Overrides .env (default: %(default)s)')
    parser.add_argument('-w', '--workers', type=int, default=1,
                        help="number of uvicorn workers. (default: %(default)s)")
    parser.add_argument('-r', '--reload', action='store_true',
                        help="reload based on reload dir. (default: %(default)s)")
    args = parser.parse_args()
    args.reload = False if args.workers > 1 else args.reload

    logger.info("Uvicorn server running on %s:%s with %s workers", args.host_ip, args.port, args.workers)
    uvicorn.run("server:music_rec", host=args.host_ip, port=args.port,
                workers=args.workers, reload=args.reload, reload_dirs=['music_rec'])
