FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip build

WORKDIR /build

# Only copy build inputs required to produce the wheel
COPY pyproject.toml pyproject.toml
COPY src src

# Build a wheel into /wheels
RUN python -m build -w -o /wheels

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create a non-root user
RUN groupadd --gid 1000 appuser || true \
 && useradd --uid 1000 --gid 1000 --shell /usr/sbin/nologin --create-home appuser || true

WORKDIR /app

# Only copy the built wheel(s) into final image; do not include source tree
COPY --from=builder /wheels/*.whl /wheels/

# Install application wheel (and runtime deps) without cache
RUN pip install --no-cache-dir /wheels/*.whl

# Switch to non-root user
USER appuser

# Expose no ports here; the entrypoint is the installed console script
ENTRYPOINT ["import-worker"]
