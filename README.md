# Question Generation — RAG MCQ Generator

A terminal-based MCQ (Multiple Choice Question) generator powered by **Groq API** (`openai/gpt-oss-120b`) and a local RAG pipeline.

## Features

- 📁 Upload documents (PDF, DOCX, TXT) and generate MCQs from them
- 🤖 LLM-powered question generation via **Groq API**
- 🏷️ Auto-tag questions with concept tags (e.g. `binary search`, `sql`, `neural network`)
- 📂 Upload existing MCQ files (JSON/CSV, any structure) and auto-tag them
- ✏️ Manually correct tags question-by-question
- 🔄 Refine questions with feedback
- 📤 Export to JSON or CSV

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/shraditya/Question-Genration.git
cd Question-Genration
```

### 2. Install dependencies
```bash
conda create -n rag_mcq python=3.10
conda activate rag_mcq
pip install -r requirements.txt
```

### 3. Configure your API key
```bash
cp .env.example .env
# Edit .env and paste your Groq API key
```
Get a free key at: https://console.groq.com

### 4. Run
```bash
python terminal_app.py
```

## Menu Options

| Option | Description |
|--------|-------------|
| 1 | Upload a document (PDF/DOCX/TXT) |
| 2 | Generate MCQs from the loaded document |
| 3 | View all MCQs |
| 4 | Refine MCQs with feedback |
| 5 | Export MCQs to JSON or CSV |
| 6 | Clear all data |
| 7 | Upload an existing MCQ file (auto-tags untagged questions) |
| 8 | Manually correct question tags |

## Project Structure

```
├── terminal_app.py       # Main terminal application
├── mcq_generator.py      # Groq API integration + auto-tagging
├── rag_system.py         # RAG pipeline with ChromaDB
├── question_tagger.py    # Keyword-based tagger
├── document_processor.py # PDF/DOCX/TXT text extraction
├── config.py             # Configuration (reads from .env)
├── requirements.txt      # Python dependencies
└── .env.example          # Environment template (copy to .env)
```
