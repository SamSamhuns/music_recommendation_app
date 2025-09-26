"""
Setup connections
"""
import base64

import requests
import psycopg
from core.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER,
    POSTGRES_PASSWORD, POSTGRES_DATABASE,
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
from contextlib import contextmanager


######## set up postgres connection #########

def get_postgres_connection() -> psycopg.Connection:
    """Return psycopg3 connection object for PostgreSQL."""
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DATABASE
    )


@contextmanager
def postgres_conn() -> callable:
    """Yield psycopg3 connection object."""
    conn = get_postgres_connection()
    try:
        yield conn
    finally:
        conn.close()


######## set up spotify api access token #########

# Use Base64 to encode the client ID and client secret
credentials = f"{SPOTIPY_CLIENT_ID}:{SPOTIPY_CLIENT_SECRET}"
credentials_base64 = base64.b64encode(credentials.encode())

# Make a request for the access token
TOKEN_URL = 'https://accounts.spotify.com/api/token'
headers = {
    'Authorization': f'Basic {credentials_base64.decode()}'
}
data = {
    'grant_type': 'client_credentials'
}
response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=100)

if response.status_code == 200:
    spot_access_token = response.json()['access_token']
    print("Spotify API Access token successfully obtained.")
else:
    print("Spotify API Access token not obtained.")
