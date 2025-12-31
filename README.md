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

### Supported File Formats

PDF and DOCX are supported via PyResparser. DOC files may require textract for full support.
