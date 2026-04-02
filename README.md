# RAG MCQ Generator (Frontend + Backend)

Full-stack application for generating MCQs from documents, auto-tagging them, checking similarity, and exporting results.

## Tech Stack

- Backend: FastAPI + Python
- Frontend: React + Vite + Tailwind CSS
- LLM provider: Groq API
- Similarity model: fine-tuned sentence-transformer

## Features

- Upload documents (PDF, DOCX, TXT) and generate MCQs
- Upload existing MCQ files (JSON/CSV)
- Auto-tag MCQs using hierarchical tags (`main_tag`, `sub_tags`)
- Similarity detection for duplicate or highly similar questions
- Export MCQs as JSON or CSV
- Interactive API docs via Swagger UI

## Prerequisites

- Python 3.10+
- Conda (recommended environment name: `rag_mcq`)
- Node.js 18+
- npm
- Groq API key

## Setup

### 1. Clone repository

```bash
git clone https://github.com/shraditya/Question-Genration.git
cd Question-Genration
```

### 2. Install backend dependencies

```bash
conda create -n rag_mcq python=3.10
conda activate rag_mcq
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Configure environment

Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_PATH=/Users/k/rag_questions/similiarty /mcq_intent_model
PORT=8000
DEBUG=False
```

## Run the Application

### Option A: Start both frontend and backend

```bash
./start.sh
```

### Option B: Start manually in separate terminals

Terminal 1 (backend):

```bash
conda activate rag_mcq
python run_backend.py
```

Terminal 2 (frontend):

```bash
cd frontend
npm run dev
```

## URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Key Project Structure

```text
backend/
  api.py                FastAPI application
  models.py             Pydantic request/response models
frontend/
  src/                  React app pages/components/services
run_backend.py          Backend entrypoint (project-root safe imports)
start.sh                Starts backend + frontend together
terminal_app.py         Legacy terminal workflow
requirements.txt        Python dependencies
```

## Additional Docs

- START_HERE.md
- QUICKSTART.md
- SETUP_REACT.md
- TROUBLESHOOTING.md

## Notes

- Similarity features require a valid model directory in `MODEL_PATH`.
- CORS is configured for local frontend dev servers.
- If port 3000 or 8000 is occupied, stop the running process and restart.
