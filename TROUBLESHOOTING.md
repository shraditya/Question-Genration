# Troubleshooting Guide

## Quick Diagnosis

Run this test script first:
```bash
cd /Users/k/rag_questions
python test_backend.py
```

This will check all dependencies and configuration.

---

## Common Issues

### 1. "Failed to upload MCQ file"

**Symptoms**: Error when uploading JSON/CSV files in the frontend

**Solutions**:

#### A. Backend not running
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
python run_backend.py
```

#### B. CORS errors (check browser console)
Open browser DevTools (F12) → Console. If you see CORS errors:

Edit `backend/api.py` line ~52 and add your frontend URL:
```python
allow_origins=["http://localhost:3000", "http://localhost:5173", "YOUR_URL_HERE"],
```

#### C. File format issues
Make sure your file is valid JSON or CSV:

**Valid JSON format:**
```json
{
  "mcqs": [
    {
      "question": "Question text?",
      "options": {"A": "Opt1", "B": "Opt2", "C": "Opt3", "D": "Opt4"},
      "correct_answer": "A",
      "explanation": "Explanation"
    }
  ]
}
```

**Test with sample file:**
```bash
# Use the provided sample
# Upload sample_mcqs.json in the frontend
```

#### D. Check backend logs
Look at the terminal where you ran `python run_backend.py`

You should see detailed logs like:
```
📂 Received file: test.json, Content-Type: application/json
✅ Successfully parsed as JSON
📋 Found key 'mcqs' with 3 items
✅ Normalized 3 MCQs successfully
```

---

### 2. "System not working" / Backend won't start

**Solution 1: Check imports**
```bash
python test_backend.py
```

Look for any ❌ marks. Common issues:

**Missing GROQ_API_KEY:**
```bash
# Create/edit .env file
echo "GROQ_API_KEY=your_key_here" > .env
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**Solution 2: Run from correct directory**
```bash
# Always run from project root
cd /Users/k/rag_questions
python run_backend.py
```

**Solution 3: Check Python version**
```bash
python --version  # Should be 3.8+
```

---

### 3. Frontend won't start

**Solution 1: Install dependencies**
```bash
cd /Users/k/rag_questions/frontend
rm -rf node_modules package-lock.json
npm install
```

**Solution 2: Check Node version**
```bash
node --version  # Should be 18+
```

**Solution 3: Port already in use**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Then start again
npm run dev
```

---

### 4. "Connection refused" / API errors

**Symptoms**: Frontend can't connect to backend

**Check 1: Is backend running?**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","rag_system":true,"mcq_generator":true,"similarity_model":false}
```

**Check 2: Port mismatch**
Make sure:
- Backend runs on port 8000
- Frontend runs on port 3000
- Vite proxy is configured correctly

**Check 3: Firewall/Network**
```bash
# Test locally
curl http://localhost:8000/health

# If that works but browser doesn't, check browser console for errors
```

---

### 5. Import errors in backend

**Error**: `ModuleNotFoundError: No module named 'document_processor'`

**Solution**:
```bash
# Always run from project root
cd /Users/k/rag_questions
python run_backend.py  # NOT: python backend/api.py
```

The `run_backend.py` script sets up paths correctly.

---

### 6. Similarity model not found

**Error**: Similarity checking fails

**This is OK if you don't have the model**. The app works without it, you just can't use similarity checking.

**To fix**:
1. Train your similarity model (outside scope)
2. Set `MODEL_PATH` in `.env`:
```bash
MODEL_PATH=/path/to/your/similarity/model
```

---

### 7. MCQ generation fails

**Check 1: GROQ_API_KEY**
```bash
# In .env file
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

**Check 2: Document uploaded?**
Make sure you uploaded a document first before generating MCQs.

**Check 3: API rate limits**
Groq has rate limits. Wait a moment and try again.

---

### 8. Auto-tagging fails

**Same as MCQ generation** - check GROQ_API_KEY and rate limits.

---

## Step-by-Step Startup Guide

### Clean Start:

```bash
# 1. Go to project root
cd /Users/k/rag_questions

# 2. Check environment
cat .env  # Should have GROQ_API_KEY

# 3. Test backend components
python test_backend.py

# 4. Start backend
python run_backend.py
# Leave this terminal open

# 5. In a NEW terminal, start frontend
cd /Users/k/rag_questions/frontend
npm run dev
# Leave this terminal open

# 6. Open browser
# Go to http://localhost:3000
```

---

## Using the Startup Script

The easiest way (starts both automatically):

```bash
cd /Users/k/rag_questions
./start.sh
```

Press Ctrl+C to stop both servers.

---

## Debugging Tips

### 1. Check Backend Logs
Look for:
- ✅ marks = things working
- ❌ marks = errors
- Detailed file upload info

### 2. Check Browser Console
Press F12 in browser:
- Console tab: JavaScript errors
- Network tab: API request/response details

### 3. Test API Directly
Visit: http://localhost:8000/docs

Try uploading a file through the interactive API docs.

### 4. Minimal Test
```bash
# Test if backend responds
curl http://localhost:8000/health

# Test file upload
curl -X POST http://localhost:8000/upload-mcq-file \
  -F "file=@sample_mcqs.json"
```

---

## Still Having Issues?

### Collect This Information:

1. **Run test script:**
```bash
python test_backend.py > test_output.txt 2>&1
```

2. **Check Python version:**
```bash
python --version
```

3. **Check Node version:**
```bash
node --version
```

4. **Backend logs** (copy terminal output)

5. **Browser console errors** (F12 → Console tab)

6. **Error message** from frontend (screenshot)

### Quick Reset:

```bash
# Stop all servers
killall python node

# Clean frontend
cd /Users/k/rag_questions/frontend
rm -rf node_modules package-lock.json
npm install

# Restart
cd /Users/k/rag_questions
./start.sh
```

---

## Success Checklist

- [ ] `python test_backend.py` shows all ✅
- [ ] `.env` file exists with GROQ_API_KEY
- [ ] Backend starts without errors
- [ ] http://localhost:8000/health returns JSON
- [ ] http://localhost:8000/docs loads
- [ ] Frontend starts without errors  
- [ ] http://localhost:3000 loads
- [ ] Can upload sample_mcqs.json successfully
- [ ] Dashboard shows system status as healthy

If all checked, system is working! 🎉
