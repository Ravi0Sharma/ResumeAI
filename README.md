# ResumeAI

ResumeAI is a fullstack project that analyzes resumes and returns a **score + actionable improvement tips**.
The frontend is built with **React (Vite)** and the backend is a **FastAPI** server that can:

- **Parse resume files** via `/parse` (deterministic scoring from extracted fields)
- **Run LLM-based matching** between resume + job description via `/analyze` (prompt → model → validated JSON)

## Screenshots (add your own links)

> Replace the links below with your real images (GitHub assets, Imgur, etc).

- **Landing page**: `![Landing page](<ADD_LANDING_IMAGE_URL_HERE>)`
- **Result page**: `![Result page](<ADD_RESULT_IMAGE_URL_HERE>)`

## Architecture (quick)

### Frontend (React / Vite)

- Uploads a resume (PDF/DOC/DOCX) to the API (`POST /parse`)
- Displays the **score** and **tips** on the result view

### Backend (FastAPI)

There are two main flows:

- **`POST /parse`**: accepts a file (multipart), extracts text and normalizes fields → computes **score + tips deterministically**
- **`POST /analyze`**: accepts `cv_text` + `job_text`, builds a prompt, calls **Ollama**, and requires the model to return **pure JSON** following a schema

## API: prompt → score pipeline (`/analyze`)

Pipeline at a glance:

- The API builds a prompt that forces the model to respond with **valid JSON**: `score (0–1000)`, `tips[]`, and optional `analysis`.
- The API calls Ollama at `POST /api/generate` with `model` from `OLLAMA_MODEL`.
- The response is **parsed as JSON** and validated (score range, tip shape). If output is invalid, the API returns an error (`INVALID_MODEL_OUTPUT`).

## Model training (and data)

This is the setup used for the model in this project:

- **Data**: **synthetically generated data** (synthetic resumes + job descriptions + labels/tips) to iterate quickly without personal data.
- **Training**: **Google Colab** (GPU).
- **Fine-tuning**: **Unsloth**.
- **Base model** (starting point):

```python
model_name = "unsloth/Phi-3-mini-4k-instruct-bnb-4bit"
```

After training, the model can be exported and run locally via **Ollama**

> Note: In the codebase, the model is selected by `OLLAMA_MODEL`

## Docker / Compose

Everything runs in containers via Docker Compose:

- **`ollama`**: runs the model (persistent volume)
- **`api`**: FastAPI (talks to `ollama` over the internal Docker network)
- **`client`**: Vite dev server

Start everything:

```bash
docker compose up --build
```

Endpoints:

- **API**: `http://localhost:8000`
- **Ollama**: `http://localhost:11434`
- **Client**: `http://localhost:5173`


## File formats

- **`/parse`** effectively supports **PDF + DOCX** (text extraction via `pdfminer` and `python-docx`).
- `.doc` is listed as allowed by the API, but the current parser does not handle `.doc` (you’d need to add an additional extractor).
