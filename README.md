# Question Generation - RAG MCQ Generator

A document-to-question workflow with tagging and similarity review in the terminal app.

## Features

- 📁 Upload documents (PDF, DOCX, TXT) and generate MCQs from them
- 🤖 LLM-powered question generation via **Groq API**
- 🏷️ Auto-tag questions with hierarchical tags: `main_tag` + `sub_tags`
- 📂 Upload existing MCQ files (JSON/CSV, flexible structures)
- 🔄 Refine questions with feedback
- 🔍 Similarity check using fine-tuned sentence-transformer model
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

### 4. Run the terminal app
```bash
python terminal_app.py
```

### 5. Similarity model path
By default the app loads:

`/Users/k/rag_questions/similiarty /mcq_intent_model`

You can override with:

```bash
export MODEL_PATH=/absolute/path/to/your/fine_tuned_model
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
| 7 | Upload an existing MCQ file (JSON/CSV) |
| 8 | Auto tag MCQs (`main_tag` + `sub_tags`) |
| 9 | Similarity check |

## JSON Output Format

When exporting JSON, the output keeps hierarchical tags and omits legacy `category`/`tags` fields.

Example:

```json
{
	"question": "What is the capital of France?",
	"options": {
		"A": "London",
		"B": "Berlin",
		"C": "Paris",
		"D": "Madrid"
	},
	"correct_answer": "Paris",
	"explanation": "",
	"main_tag": "Social Sciences",
	"sub_tags": ["Geography", "European capitals", "France"]
}
```

## Project Structure

```
├── terminal_app.py       # Main terminal application
├── mcq_generator.py      # Groq API integration + hierarchical tagging
├── rag_system.py         # RAG pipeline with ChromaDB
├── question_tagger.py    # Local hierarchical question tagger
├── document_processor.py # PDF/DOCX/TXT text extraction
├── config.py             # Configuration (reads from .env)
├── requirements.txt      # Python dependencies
└── .env.example          # Environment template (copy to .env)
```
