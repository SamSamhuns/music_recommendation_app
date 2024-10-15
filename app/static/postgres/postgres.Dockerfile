FROM postgres:16.4

# Install pgvector
RUN apt update && apt install -y --no-install-recommends \
    postgresql-16-pgvector \
    && rm -rf /var/lib/apt/lists/*