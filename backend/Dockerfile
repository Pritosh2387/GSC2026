FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps required for some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app

# Install Python dependencies from whichever requirements file is present
RUN pip install --upgrade pip \
        && if [ -f backend/requirements.txt ]; then \
                 pip install --no-cache-dir -r backend/requirements.txt; \
             elif [ -f requirements.txt ]; then \
                 pip install --no-cache-dir -r requirements.txt; \
             else \
                 echo "No requirements file found; continuing without installing Python packages"; \
             fi

EXPOSE 8000
ENV PORT 8000

CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
