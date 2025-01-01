# syntax=docker/dockerfile:1
FROM python:3.11

WORKDIR /src

RUN pip install poetry
RUN apt update && apt install -y default-libmysqlclient-dev && apt clean

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

COPY watchapedia ./watchapedia
COPY alembic.ini ./alembic.ini