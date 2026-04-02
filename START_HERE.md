# 🚀 Start Here - Quick Setup

## Prerequisites
- Conda environment `rag_mcq` must be created
- Node.js 18+ installed

## Step 1: Start Backend

**Option A: Use startup script (recommended)**
```bash
cd /Users/k/rag_questions
./start.sh
```

**Option B: Manual start**
```bash
cd /Users/k/rag_questions
conda activate rag_mcq
python run_backend.py
```

Leave this terminal open. Backend will run on http://localhost:8000

## Step 2: Start Frontend

Open a **NEW terminal**:

```bash
cd /Users/k/rag_questions/frontend

# First time only:
npm install

# Start dev server:
npm run dev
```

Leave this terminal open. Frontend will run on http://localhost:3000

## Step 3: Open Browser

Go to: **http://localhost:3000**

## ✅ Verify Setup

1. **Backend Health**: http://localhost:8000/health
   - Should return JSON with `"status": "healthy"`

2. **API Docs**: http://localhost:8000/docs
   - Should show interactive API documentation

3. **Frontend**: http://localhost:3000
   - Should show dashboard with system status

## 🎯 Quick Test

1. Go to http://localhost:3000
2. Click "Upload" in navigation
3. Click "Load MCQ File" tab
4. Upload `sample_mcqs.json` from the project root
5. You should see "Loaded 3 questions"

## 🛑 Stop Servers

**If using start.sh:**
- Press `Ctrl+C` in the terminal

**If started manually:**
- Press `Ctrl+C` in each terminal (backend and frontend)

## ❌ Troubleshooting

### "Failed to load system status"
- Backend is not running
- Run: `curl http://localhost:8000/health`
- If it fails, backend is down

**Solution:**
```bash
# Make sure conda env is activated
conda activate rag_mcq

# Start backend
python run_backend.py
```

### "Failed to upload MCQ file"
- Check browser console (F12) for errors
- Check backend terminal for logs
- Make sure file is valid JSON or CSV

**Test with sample:**
```bash
# Use the provided sample file
# Upload: /Users/k/rag_questions/sample_mcqs.json
```

### CORS errors
- Make sure backend is on port 8000
- Make sure frontend is on port 3000
- Check browser console for exact error

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

## 📚 Next Steps

Once running:
1. **Upload Document** - Upload PDF/DOCX/TXT to generate MCQs
2. **Generate MCQs** - Create questions using RAG
3. **Auto Tag** - Add AI-generated hierarchical tags
4. **Check Similarity** - Find duplicate questions
5. **Export** - Download as JSON or CSV

## 🔧 Important Notes

- **Always use conda environment `rag_mcq`** for backend
- Backend runs on port 8000 (don't change)
- Frontend runs on port 3000 (don't change)
- Check `.env` file has `GROQ_API_KEY`

## 📖 Documentation

- **Full setup**: `SETUP_REACT.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **Quick start**: `QUICKSTART.md`

---

**Current Status:**
- ✅ Backend running: Check with `curl http://localhost:8000/health`
- ⏳ Frontend: You need to start it manually (see Step 2 above)
