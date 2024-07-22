FROM python:3.12-slim-bullseye AS base

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

FROM base AS dev

COPY ./ /app
WORKDIR /app

CMD ["uvicorn", "--port", "8080", "--host", "0.0.0.0", "src.main:app"]
