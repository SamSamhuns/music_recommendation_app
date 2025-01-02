# Music Analysis: Recommendation System, Vocal Isolation, and Music Generation

[![Python 3.10](https://img.shields.io/badge/python-3.10-green.svg)](https://www.python.org/downloads/release/python-3100/)[![Python 3.11](https://img.shields.io/badge/python-3.11-green.svg)](https://www.python.org/downloads/release/python-3110/)[![Python 3.12](https://img.shields.io/badge/python-3.12-green.svg)](https://www.python.org/downloads/release/python-3120/)

Tested with `Docker version v27.0.3` and `Docker Compose version v2.29.1`.

Backend with fastapi+uvicorn for music database analysis with LLMs and PostgreSQL queries.

- [Music Analysis: Recommendation System, Vocal Isolation, and Music Generation](#music-analysis-recommendation-system-vocal-isolation-and-music-generation)
  - [API Architecture Setup](#api-architecture-setup)
  - [Setup](#setup)
    - [1. Create .env file](#1-create-env-file)
    - [2. Create shared volumes directory](#2-create-shared-volumes-directory)
  - [Running the log analysis service](#running-the-log-analysis-service)
    - [Option A) Docker Compose](#option-a-docker-compose)
      - [Note:](#note)
    - [Option B) Docker and local virtual env](#option-b-docker-and-local-virtual-env)
      - [Option Bi) Uvicorn server with fastapi with Docker](#option-bi-uvicorn-server-with-fastapi-with-docker)
      - [Option Bii) Uvicorn server with fastapi with venv](#option-bii-uvicorn-server-with-fastapi-with-venv)
    - [Running PGAdmin](#running-pgadmin)
    - [Optional: frontend with streamlit](#optional-frontend-with-streamlit)
    - [Optional: expose app through ngrok docker for sharing localhost on the internet](#optional-expose-app-through-ngrok-docker-for-sharing-localhost-on-the-internet)
  - [Testing](#testing)
  - [For Developers](#for-developers)
    - [To change/add/delete new log table schemas](#to-changeadddelete-new-log-table-schemas)
  - [References](#references)

## API Architecture Setup

[<img src="app/static/images/log analyzer.drawio.png">]()

## Setup

### 1. Create .env file

Create a `.env` file with the following keys with updated values for unames and pass:

```yaml
# set to ERROR for deployment
DEBUG_LEVEL=DEBUG
# http api server
API_SERVER_PORT=8080
# spotify api keys
CLIENT_ID=<CLIENT_ID>
CLIENT_SECRET=<CLIENT_SECRET>
# postgresql
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=default
# postgres admin
PGADMIN_PORT=8888
PGADMIN_DEFAULT_EMAIL=<PGADMIN_DEFAULT_EMAIL>
PGADMIN_DEFAULT_PASSWORD=<PGADMIN_DEFAULT_PASSWORD>
```

### 2. Create shared volumes directory

```shell
mkdir -p volumes/music_analysis
mkdir -p volumes/store
```

## Running the log analysis service

There are two options for running the analysis service. Both require `docker compose` (Available from the [official docker site](https://docs.docker.com/compose/install/)). `$docker-compose ...` style commands have been depreciated.

### Option A) Docker Compose

Note: some services are set to bind to all addresses which should be changed in a production environment.

```shell
# build all required containers
docker compose build
# start all services
docker compose up -d
```

The server will be available at <http://localhost:8080> if using the default port.

#### Note:

When changing settings in `docker-compose.yaml` for the mongodb service, the existing docker and shared volumes might have to be purged i.e. when changing replicaset name.

<p style="color:red;">WARNING: This will delete all existing user, document, and vector records.</p>

```shell
docker-compose down
docker volume rm $(docker volume ls -q)
rm -rf volumes/pg_data
```

### Option B) Docker and local virtual env

```shell
# build all required containers
docker compose build
# start postgres server & pgadmin server
docker compose up -d postgres pgadmin
```

#### Option Bi) Uvicorn server with fastapi with Docker

Build server container and start server at HTTP port EXPOSED_HTTP_PORT

```shell
bash scripts/build_docker.sh
bash scripts/run_docker.sh -p EXPOSED_HTTP_PORT
```

The server will be available at <http://localhost:8080> if using the default port.

#### Option Bii) Uvicorn server with fastapi with venv

Install requirements inside venv or conda environment

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start server at HTTP port EXPOSED_HTTP_PORT. Note the host names must contain addresses when using docker microservices and the fastapi+uvicorn server outside the docker compose environment.

```shell
python app/server.py -p EXPOSED_HTTP_PORT
```

The server will be available at <http://localhost:8080> if using the default port.

### Running PGAdmin

Set the PGAdmin client in the host name/address to:

```
host.docker.internal
```

### Optional: frontend with streamlit

[<img src="app/static/images/streamlit_example.png">]()

```shell
pip install streamlit==1.38.0
streamlit run app/streamlit_frontend.py
```

### Optional: expose app through ngrok docker for sharing localhost on the internet

WARNING: Never use for production

```bash
# start log analyzer with python
# sign up for ngrok account at https://ngrok.com/
# https://ngrok.com/docs/using-ngrok-with/docker/
docker pull ngrok/ngrok
# for linux systems
docker run --net=host -it -e NGROK_AUTHTOKEN=<NGROK_AUTHTOKEN> ngrok/ngrok:latest http <EXPOSED_HTTP_PORT>
# for MacOS and windows
docker run -it -e NGROK_AUTHTOKEN=<NGROK_AUTHTOKEN> ngrok/ngrok:latest http host.docker.internal:<EXPOSED_HTTP_PORT>
```

## Testing

Note: all the microservices must already be running with docker compose.

Install requirements:

```shell
pip install -r tests/requirements.txt
```

Run tests:

```shell
pytest tests/
```

Generating coverage reports

```shell
coverage run -m pytest tests/
coverage report -m -i
```

## For Developers

### To change/add/delete new log table schemas

The new SQL table should also be created through the PHPMyAdmin GUI/mysql command line inside the mariadb container.

The following files must be edited.

-   Edit `app/static/sql/init.sql` for changing/adding log table schema
-   Edit `app/models/model.py` to add/edit the LogFileType
-   Edit `app/api/log_format/log_parser.py` for parsing logs
-   Edit `app/core/setup.py` for adding table schema and data sample info for text2sql conversion

Editing Tests

-   Edit `tests/conftests.py` for setting the correct values for the test database
-   Edit `tests/api/test_mysql_api.py` for setting the correct values for the test database


## References

-   [Spotify API](https://developer.spotify.com/documentation/web-api/reference/get-recommendations)
-   [pgvector](https://github.com/pgvector/pgvector)
-   [Text-to-SQL by LLMs: A Benchmark Evaluation](https://arxiv.org/pdf/2308.15363)