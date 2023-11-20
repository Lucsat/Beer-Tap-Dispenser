FROM python:3.11.4-alpine

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
         openssl-dev libffi-dev gcc musl-dev python3-dev postgresql-dev bash
RUN pip install --upgrade pip setuptools wheel
RUN pip install poetry

COPY /pyproject.toml /opt/app
RUN poetry install

RUN rm -rf /root/.cache/pip

COPY . /opt/app

