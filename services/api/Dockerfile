FROM python:3.12-slim

# uv ikilisini resmi imajdan al
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_PREFERENCE=only-system \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Önce kilit + manifest → katman cache
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

# Render PORT enjekte eder; lokal/8000 fallback start.sh'ta.
EXPOSE 8000
CMD ["sh", "start.sh"]
