# RAG MCQ Generator - React Frontend Setup

## Overview

A modern React frontend with FastAPI backend for generating, tagging, and managing MCQs using RAG and AI.

## Architecture

```
rag_questions/
├── backend/
│   ├── api.py              # FastAPI backend
│   └── models.py           # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── pages/         # React pages
│   │   ├── services/      # API service
│   │   ├── App.jsx        # Main app
│   │   └── main.jsx       # Entry point
│   ├── package.json
│   └── vite.config.js
├── terminal_app.py         # Original terminal app
└── app.py                  # Old Flask API
```

## Features

✅ **Document Upload** - PDF, DOCX, TXT, or text input  
✅ **MCQ Generation** - Generate MCQs from documents using RAG  
✅ **Hierarchical Auto-Tagging** - Main tags + sub-tags with AI  
✅ **Similarity Detection** - Find duplicates using fine-tuned model  
✅ **MCQ File Upload** - Load existing MCQ files (JSON/CSV)  
✅ **Export** - Download as JSON or CSV  
✅ **Interactive UI** - Modern, responsive React interface  
✅ **Real-time Updates** - Live stats and progress tracking  

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

## Backend Setup

### 1. Install Python Dependencies

```bash
cd /Users/k/rag_questions

# Install backend dependencies
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart
```

### 2. Set Environment Variables

Create/update `.env` file:

```bash
# Groq API Key (required)
GROQ_API_KEY=your_groq_api_key_here

# Model Path (required for similarity checking)
MODEL_PATH=/Users/k/rag_questions/similiarty /mcq_intent_model

# Optional
PORT=8000
DEBUG=False
```

### 3. Start Backend Server

```bash
# From the project root
python backend/api.py

# Or with uvicorn
uvicorn backend.api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API Docs: `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend

# Install dependencies
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The React app will be available at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build

# Preview production build
npm run preview
```

## Usage

### 1. **Upload a Document**
- Click "Upload" in the navigation
- Choose to upload a file (PDF/DOCX/TXT) or paste text
- Or upload an existing MCQ file (JSON/CSV)

### 2. **Generate MCQs**
- Click "Generate" in the navigation
- Select number of questions (1-30)
- Click "Generate MCQs"
- MCQs will be created using RAG

### 3. **Auto-Tag MCQs**
- Click "Auto Tag" in the navigation
- Click "Auto Tag All MCQs"
- AI will generate main tags + sub-tags for each MCQ

### 4. **Check Similarity**
- Click "Similarity" in the navigation
- Adjust threshold slider (0.50 - 0.95)
- Click "Check Similarity"
- View duplicates and similar pairs

### 5. **Export MCQs**
- Click "Export" in the navigation
- Choose JSON or CSV format
- Click "Export" to download

## API Endpoints

### Document Management
- `POST /upload-text` - Upload text document
- `POST /upload-file` - Upload file (PDF/DOCX/TXT)
- `POST /upload-mcq-file` - Upload MCQ file (JSON/CSV)

### MCQ Operations
- `POST /generate-mcqs` - Generate MCQs from document
- `GET /mcqs` - Get current MCQs
- `POST /auto-tag` - Auto-tag MCQs with AI
- `POST /similarity-check` - Check MCQ similarity
- `POST /refine-mcqs` - Refine MCQs with feedback

### Export & Utility
- `POST /export` - Export MCQs (JSON/CSV)
- `DELETE /clear` - Clear all data
- `GET /health` - Health check
- `GET /config` - Get configuration

## Configuration

### Backend (`config.py`)
```python
GROQ_MODEL = "llama-3.3-70b-versatile"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
LLM_RETRIES = 3
LLM_RETRY_DELAY = 2
```

### Frontend (Vite proxy)
```javascript
// vite.config.js
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## Similarity Model

The similarity checker uses a fine-tuned sentence-transformer model:

**Path**: `/Users/k/rag_questions/similiarty /mcq_intent_model`

**Features**:
- Adaptive weighting: `answer_weight = 0.15 + 0.70 × (1 - question_sim)`
- Thresholds:
  - Duplicate: ≥ 0.90
  - Highly Similar: ≥ 0.80
  - Similar: ≥ 0.75 (configurable)

## Troubleshooting

### Backend Issues

**ImportError**:
```bash
# Make sure you're in the project root
cd /Users/k/rag_questions
python backend/api.py
```

**Model not found**:
```bash
# Check MODEL_PATH in .env
# Ensure the similarity model exists at the path
```

**CORS errors**:
- Check `allow_origins` in `backend/api.py`
- Add your frontend URL if different from localhost:3000

### Frontend Issues

**API connection failed**:
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify proxy settings in `vite.config.js`

**Dependencies not found**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Development Tips

### Hot Reload
Both backend (with `--reload`) and frontend (Vite) support hot reload.

### Debugging
- Backend: Check terminal logs
- Frontend: Use browser DevTools (F12)
- API: Visit `http://localhost:8000/docs` for interactive testing

### Adding New Features
1. Add endpoint in `backend/api.py`
2. Add API call in `frontend/src/services/api.js`
3. Create/update page component
4. Add route in `frontend/src/App.jsx`

## Tech Stack

### Backend
- FastAPI - Modern async Python framework
- Pydantic - Data validation
- SentenceTransformers - Embeddings
- ChromaDB - Vector database
- Groq - LLM API

### Frontend
- React 18 - UI library
- Vite - Build tool
- TailwindCSS - Styling
- Recharts - Data visualization
- React Router - Navigation
- Axios - HTTP client
- React Hot Toast - Notifications
- React Dropzone - File uploads

## License

This project is for educational purposes.

## Support

For issues or questions, check:
- API Docs: `http://localhost:8000/docs`
- Browser Console: F12
- Terminal logs
