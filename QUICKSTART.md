# Quick Start Guide

## 1. Install Dependencies

### Backend
```bash
cd /Users/k/rag_questions
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## 2. Configure Environment

Create `.env` file in project root:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (for similarity checking)
MODEL_PATH=/Users/k/rag_questions/similiarty /mcq_intent_model

# Optional
PORT=8000
DEBUG=False
```

## 3. Start Application

### Option A: Use Startup Script (Recommended)
```bash
./start.sh
```

This starts both backend and frontend automatically.

### Option B: Start Separately

**Terminal 1 - Backend:**
```bash
python backend/api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 5. Basic Workflow

1. **Upload Document**
   - Go to "Upload" tab
   - Upload PDF/DOCX/TXT or paste text

2. **Generate MCQs**
   - Go to "Generate" tab
   - Choose number of questions (1-30)
   - Click "Generate MCQs"

3. **Auto-Tag**
   - Go to "Auto Tag" tab
   - Click "Auto Tag All MCQs"
   - AI generates hierarchical tags

4. **Check Duplicates**
   - Go to "Similarity" tab
   - Adjust threshold
   - Click "Check Similarity"

5. **Export**
   - Go to "Export" tab
   - Choose JSON or CSV
   - Download file

## Troubleshooting

### Backend won't start
- Check `.env` file exists with GROQ_API_KEY
- Ensure all dependencies installed: `pip install -r requirements.txt`

### Frontend won't start
- Delete `node_modules` and run `npm install` again
- Check Node.js version (need 18+)

### CORS errors
- Make sure backend is running on port 8000
- Check browser console for specific errors

### Similarity model not found
- Set correct `MODEL_PATH` in `.env`
- Similarity checking will fail if model missing

## Next Steps

- Read full documentation in `SETUP_REACT.md`
- Explore API at http://localhost:8000/docs
- Check original terminal app in `terminal_app.py`
