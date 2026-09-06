# AYUConnect backend
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Production entry point (Gunicorn). In development you can override
# the command to `python run.py` for the debug server.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "run:app"]