FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Instala las dependencias del sistema necesarias para docling y procesamiento de imágenes
RUN apt-get update && \
    apt-get install -y \
    tzdata \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Define variables de entorno
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala las dependencias del proyecto usando el lockfile y la configuración
RUN --mount=type=cache,target=/app/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=/app/pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copia el código fuente del proyecto
COPY ./src/ /app/src

# Coloca los ejecutables del entorno al principio del PATH
ENV PATH="/app/.venv/bin:$PATH"

# Ejecuta la aplicación
CMD ["python", "-m", "src.main"]