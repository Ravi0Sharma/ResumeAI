# ResumeAI

## Setup

### Backend Dependencies

Install Python dependencies:
```bash
pip install -r backend/requirements.txt
```

Download required models:
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader words
```

### Ollama + FastAPI (Docker)

- Start Ollama on your host (macOS): `ollama serve` (or run the Ollama app)
- Verify available tags:

```bash
curl http://localhost:11434/api/tags
```

- Start the API:

```bash
docker-compose up --build
```

- Test `/analyze`:

```bash
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"cv_text":"my cv text","job_text":"my job text"}'
```

### Supported File Formats

PDF and DOCX are supported via PyResparser. DOC files may require textract for full support.
