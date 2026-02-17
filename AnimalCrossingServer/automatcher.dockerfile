FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip build

WORKDIR /build

COPY pyproject.toml pyproject.toml
COPY src src

RUN python -m build -w -o /wheels

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --gid 1000 appuser || true \
 && useradd --uid 1000 --gid 1000 --shell /usr/sbin/nologin --create-home appuser || true

WORKDIR /app

COPY --from=builder /wheels/*.whl /wheels/
RUN pip install --no-cache-dir /wheels/*.whl

USER appuser

ENTRYPOINT ["automatcher"]
