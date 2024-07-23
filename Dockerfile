FROM python:3.12-slim-bullseye AS base

WORKDIR /app
COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

FROM base AS dev

WORKDIR /app