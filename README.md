# ResumeAI

ResumeAI är ett fullstack-projekt som analyserar CV:n och ger ett **score + konkreta förbättringstips**.
Frontend är byggd i **React (Vite)** och backend är en **FastAPI**-server som både kan:

- **Parsa CV-filer** via `/parse` (deterministisk scoring från extraherad data)
- **Köra LLM-baserad matchning** mellan CV + jobbannons via `/analyze` (prompt → modell → validerad JSON)

## Screenshots (lägg in dina egna länkar)

> Byt ut länkarna nedan till dina riktiga bilder (GitHub assets, Imgur, etc).

- **Landing page**: `![Landing page](<ADD_LANDING_IMAGE_URL_HERE>)`
- **Result page**: `![Result page](<ADD_RESULT_IMAGE_URL_HERE>)`

## Arkitektur (kort)

### Frontend (React / Vite)

- Uploadar CV (PDF/DOC/DOCX) till API:t (`POST /parse`)
- Visar **score** och **tips** på resultatvyn

### Backend (FastAPI)

Det finns två huvudflöden:

- **`POST /parse`**: tar emot en fil (multipart), extraherar text och normaliserar fält → beräknar **score + tips deterministiskt**
- **`POST /analyze`**: tar emot `cv_text` + `job_text`, bygger en prompt, anropar **Ollama** och kräver att modellen svarar med **ren JSON** enligt schema

## API: prompt → score pipeline (`/analyze`)

Pipeline i korthet:

- Vi bygger en prompt som tvingar modellen att svara med **giltig JSON**: `score (0–1000)`, `tips[]` och optional `analysis`.
- API:t anropar Ollama på `POST /api/generate` med `model` från `OLLAMA_MODEL`.
- Svaret **parsas som JSON** och valideras (score range, tips shape). Om output inte är korrekt returneras fel (`INVALID_MODEL_OUTPUT`).

## Så tränade vi modellen (och datan)

Det här är upplägget för modellen vi använde i projektet:

- **Data**: vi använde **syntetiskt genererad data** (syntetiska CV:n + jobbannonser + labels/tips) för att kunna iterera snabbt utan persondata.
- **Träning**: gjordes i **Google Colab** för att få GPU.
- **Finetuning**: med **Unsloth**.
- **Basmodell** (som utgångspunkt):

```python
model_name = "unsloth/Phi-3-mini-4k-instruct-bnb-4bit"
```

Efter träning exporterade vi modellen och kör den lokalt via **Ollama** (för enklare inference + API-integration).

> OBS: I koden styrs vilken modell som används av `OLLAMA_MODEL` (se `docker-compose.yml` och `api/src/config.py`). Byt den till din Ollama-tag när du lagt in modellen där.

## Docker / Compose

Allt körs i containrar med Docker Compose:

- **`ollama`**: kör modellen (persistens via volume)
- **`api`**: FastAPI (pratar med `ollama` över intern Docker-network)
- **`client`**: Vite dev server

Starta allt:

```bash
docker compose up --build
```

Endpoints:

- **API**: `http://localhost:8000`
- **Ollama**: `http://localhost:11434`
- **Client**: `http://localhost:5173`

### Välj modell (Ollama)

Kolla vilka modeller/tags som finns:

```bash
curl http://localhost:11434/api/tags
```

Om du behöver hämta en modell i containern:

```bash
docker compose exec ollama ollama pull <YOUR_MODEL_TAG_HERE>
```

## Testa API

### `/parse` (fil-upload)

Frontend använder `POST http://localhost:8000/parse` med multipart upload.

### `/analyze` (CV text + jobbtext)

```bash
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"cv_text":"my cv text","job_text":"my job text"}'
```

## Filformat

- **`/parse`** stöder i praktiken **PDF + DOCX** (text extraheras med `pdfminer` och `python-docx`).
- `.doc` är listat som accepterat i API:t, men själva parsern hanterar inte `.doc` (du behöver isåfall lägga till en extra extractor).
