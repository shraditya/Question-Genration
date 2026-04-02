# RAG MCQ Generator - React Frontend

Modern React + FastAPI application for generating, tagging, and managing multiple-choice questions using RAG and AI.

## 🎯 Features

- 📄 **Document Processing** - Upload PDF, DOCX, TXT files
- 🤖 **AI MCQ Generation** - Generate questions using RAG (Retrieval-Augmented Generation)
- 🏷️ **Hierarchical Tagging** - Auto-tag with main tags + sub-tags using Groq LLM
- 🔍 **Similarity Detection** - Find duplicates using fine-tuned model with adaptive weighting
- 📊 **Interactive Dashboard** - Real-time stats and system monitoring
- 📤 **Export** - Download as JSON or CSV
- 🎨 **Modern UI** - Responsive React interface with TailwindCSS

## 📸 Screenshots

- **Dashboard**: System status, stats, quick actions
- **Upload**: Drag & drop file uploads
- **Generate**: Create MCQs from documents
- **View**: Browse, search, filter MCQs
- **Auto Tag**: AI-powered hierarchical tagging
- **Similarity**: Duplicate detection with charts
- **Export**: Download in multiple formats

## 🚀 Quick Start

**👉 See [START_HERE.md](START_HERE.md) for detailed instructions**

### TL;DR:

```bash
# Terminal 1: Backend
conda activate rag_mcq
python run_backend.py

# Terminal 2: Frontend
cd frontend
npm install  # first time only
npm run dev

# Open browser: http://localhost:3000
```

## 📋 Requirements

- Python 3.8+ with conda environment `rag_mcq`
- Node.js 18+
- Groq API key (for MCQ generation and tagging)

## 🏗️ Architecture

```
Frontend (React) <---> Backend (FastAPI) <---> Services
   Port 3000              Port 8000             - RAG System (ChromaDB)
                                                - MCQ Generator (Groq)
                                                - Similarity Model (SentenceTransformer)
```

## 📁 Project Structure

```
rag_questions/
├── backend/              # FastAPI backend
│   ├── api.py           # Main API server
│   └── models.py        # Pydantic models
├── frontend/            # React frontend
│   ├── src/
│   │   ├── pages/      # React pages
│   │   ├── services/   # API client
│   │   └── App.jsx     # Main app
│   └── package.json
├── terminal_app.py      # Original terminal version
├── sample_mcqs.json     # Sample file for testing
├── run_backend.py       # Backend starter script
├── start.sh             # Startup script (both servers)
└── START_HERE.md        # Quick start guide
```

## 🔧 Tech Stack

**Backend:**
- FastAPI - Modern async Python web framework
- Pydantic - Data validation
- SentenceTransformers - Embeddings & similarity
- ChromaDB - Vector database
- Groq - LLM API
- LangChain - RAG framework

**Frontend:**
- React 18 - UI library
- Vite - Build tool & dev server
- TailwindCSS - Utility-first CSS
- React Router - Routing
- Axios - HTTP client
- Recharts - Charts & visualization
- React Dropzone - File uploads
- React Hot Toast - Notifications

## 📊 API Endpoints

### Documents
- `POST /upload-text` - Upload text content
- `POST /upload-file` - Upload PDF/DOCX/TXT
- `POST /upload-mcq-file` - Load existing MCQ file

### MCQ Operations
- `POST /generate-mcqs` - Generate from document
- `GET /mcqs` - Get current MCQs
- `POST /auto-tag` - Auto-tag with AI
- `POST /similarity-check` - Find duplicates
- `POST /refine-mcqs` - Refine with feedback

### Export & Utilities
- `POST /export` - Export as JSON/CSV
- `DELETE /clear` - Clear all data
- `GET /health` - Health check
- `GET /config` - Get configuration

**Interactive Docs**: http://localhost:8000/docs

## 🎯 Usage Workflow

1. **Upload Document**
   - Go to "Upload" tab
   - Upload PDF/DOCX/TXT or paste text
   - System processes into chunks

2. **Generate MCQs**
   - Go to "Generate" tab
   - Select number of questions (1-30)
   - Click "Generate MCQs"
   - AI creates questions using RAG

3. **Auto-Tag**
   - Go to "Auto Tag" tab
   - Click "Auto Tag All MCQs"
   - AI generates hierarchical tags

4. **Check Duplicates**
   - Go to "Similarity" tab
   - Adjust threshold (0.50-0.95)
   - View similar/duplicate pairs

5. **Export**
   - Go to "Export" tab
   - Choose JSON or CSV
   - Download file

## 🔬 Similarity Algorithm

Uses fine-tuned sentence-transformer with **adaptive weighting**:

```python
answer_weight = 0.15 + 0.70 × (1 - question_sim)
final_sim = answer_weight × answer_sim + question_weight × question_sim
```

**Classification:**
- Duplicate: ≥ 0.90
- Highly Similar: ≥ 0.80
- Similar: ≥ 0.75 (configurable)

## 🏷️ Hierarchical Tagging

Each MCQ receives:
- **Main Tag**: Primary category (e.g., "Programming")
- **Sub Tags**: Up to 3 specific topics (e.g., ["Python", "Functions", "OOP"])
- **Confidence**: AI confidence score
- **Difficulty**: easy/medium/hard

## 📝 Configuration

### Environment Variables (.env)
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
MODEL_PATH=/Users/k/rag_questions/similiarty /mcq_intent_model
PORT=8000
DEBUG=False
```

### Backend (config.py)
```python
GROQ_MODEL = "llama-3.3-70b-versatile"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
LLM_RETRIES = 3
```

## 🧪 Testing

**Test backend:**
```bash
python test_backend.py
```

**Test with sample file:**
1. Start servers
2. Go to http://localhost:3000
3. Upload → Load MCQ File
4. Select `sample_mcqs.json`

**Test API directly:**
```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Common issues:**
- "Failed to load system status" → Backend not running
- "Failed to upload MCQ file" → Check file format or backend logs
- CORS errors → Check backend is on port 8000
- Import errors → Use conda env `rag_mcq`

## 📚 Documentation

- **START_HERE.md** - Quick start guide
- **SETUP_REACT.md** - Full setup instructions
- **TROUBLESHOOTING.md** - Common issues & solutions
- **QUICKSTART.md** - Condensed setup guide

## 🤝 Original Version

The terminal-based version is still available:
```bash
conda activate rag_mcq
python terminal_app.py
```

## 📄 License

Educational purposes

## 🙏 Acknowledgments

Built with:
- FastAPI
- React
- Groq API
- SentenceTransformers
- ChromaDB
- LangChain

---

**Made with ❤️ for RAG-powered MCQ generation**
