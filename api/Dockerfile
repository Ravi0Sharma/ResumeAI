FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install API + parsing pipeline dependencies.
# Build context is repo root (see docker-compose.yml), so paths are prefixed with `api/` and `backend/`.
COPY api/requirements.txt /app/api-requirements.txt
COPY backend/requirements.txt /app/backend-requirements.txt
RUN pip install --no-cache-dir -r /app/api-requirements.txt -r /app/backend-requirements.txt \
    && python -m spacy download en_core_web_sm \
    && python -m nltk.downloader words

COPY api/src /app/src
COPY backend /app/backend

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]



