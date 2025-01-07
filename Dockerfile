# syntax=docker/dockerfile:1
FROM python:3.11

WORKDIR /src

RUN pip install poetry
RUN apt update && apt install -y default-libmysqlclient-dev && apt clean

COPY pyproject.toml poetry.lock ./
COPY README.md ./README.md
RUN poetry install --no-root

COPY watchapedia ./watchapedia
COPY alembic.ini ./alembic.ini