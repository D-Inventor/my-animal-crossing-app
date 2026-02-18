FROM python:3.14-slim AS builder

RUN mkdir -p /app/src
WORKDIR /app

RUN groupadd -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup appuser && \
    mkdir -p /opt/venvs && \
    chown -R appuser:appgroup /opt/venvs /app

USER appuser
ENV VIRTUAL_ENV=/opt/venvs/my-app \
    PATH="/opt/venvs/my-app/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

RUN pip install --upgrade pip build

COPY --chown=appuser:appgroup pyproject.toml pyproject.toml

RUN pip install --no-cache-dir -e .

COPY --chown=appuser:appgroup src/api src/api

USER appuser
ENTRYPOINT ["sh", "-c", "api-migrate && exec api"]
