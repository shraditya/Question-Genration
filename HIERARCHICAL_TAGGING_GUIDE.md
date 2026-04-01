# 🏷️ Hierarchical Tagging System - Complete Guide

## ✅ Implementation Complete!

Both **keyword-based** and **LLM-based** taggers now support **hierarchical tags** with:
- **1 Main Category** (e.g., "Technology", "Science", "Geography")
- **2-3 Sub-Tags** (e.g., "Machine Learning", "Deep Learning", "Computer Vision")

---

## 📊 System Architecture

### 1. **Keyword-Based Tagger** ([question_tagger.py](question_tagger.py))

**How it works:**
- Analyzes question text + correct answer using keyword matching
- Scores topics based on keyword frequency and weight
- Returns hierarchical tags automatically

**Taxonomy Structure:**
```python
"Technology" → {
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Computer Vision",
    "Natural Language Processing",
    "Transformers"
}

"Neural Networks" → {
    "Optimization",
    "Attention Mechanism",
    "Sequence Modeling",
    "Training Techniques"
}

"Data Science" → {
    "Data Preprocessing",
    "Evaluation Metrics",
    "Statistical Analysis"
}
```

**Usage:**
```python
from question_tagger import QuestionTagger

tagger = QuestionTagger()
tagged = tagger.tag_questions(questions)

# Each question now has:
# {
#     "main_tag": "Technology",
#     "sub_tags": ["Deep Learning", "Computer Vision"],
#     "tags": ["Technology", "Deep Learning", "Computer Vision"],
#     "category": "Technology",
#     "difficulty": "medium",
#     "bloom_category": "understand",
#     "confident": True
# }
```

**Pros:**
✅ Fast - no API calls
✅ Free - no rate limits
✅ Deterministic results
✅ Works offline

**Cons:**
❌ Limited to predefined keywords
❌ Best for technical/AI content
❌ May miss general knowledge topics

---

### 2. **LLM-Based Tagger** ([mcq_generator.py](mcq_generator.py))

**How it works:**
- Uses Groq LLM (`llama-3.3-70b-versatile`)
- Analyzes question text + correct answer semantically
- Returns hierarchical tags with better accuracy

**Taxonomy Structure:**
```python
TAG_TAXONOMY = {
    "Science": ["Biology", "Chemistry", "Physics", ...],
    "Geography": ["Physical Geography", "Capitals & Cities", ...],
    "History": ["Ancient History", "World Wars", ...],
    "Technology": ["AI", "Machine Learning", "Deep Learning", ...],
    "Mathematics": ["Algebra", "Geometry", "Calculus", ...],
    "Literature": ["Poetry", "Fiction", "Drama", ...],
    "Arts & Culture": ["Music", "Film", "Theater", ...],
    "Sports & Games": ["Football", "Cricket", "Chess", ...],
    "General Knowledge": ["Current Affairs", "Trivia", ...]
}
```

**Usage:**
```python
from mcq_generator import MCQGenerator

generator = MCQGenerator()
tagged = generator.llm_tag_questions(questions)

# Each question now has:
# {
#     "main_tag": "Technology",
#     "sub_tags": ["Artificial Intelligence", "Machine Learning"],
#     "tags": ["Technology", "Artificial Intelligence", "Machine Learning"],
#     "category": "Technology"
# }
```

**Pros:**
✅ Semantic understanding
✅ Works for any domain
✅ More accurate
✅ Handles general knowledge well

**Cons:**
❌ Requires API calls (costs)
❌ Non-deterministic
❌ Requires internet
❌ Has rate limits

---

## 🚀 Using in Terminal App

The [terminal_app.py](terminal_app.py) has been updated to display hierarchical tags beautifully:

### Run the App:
```bash
python terminal_app.py
```

### Upload MCQ File (Option 7):
```
7. 📂 Upload MCQ File (JSON/CSV)
```
- Loads your questions
- **Automatically tags with LLM hierarchical tagger**
- Shows: `Main Category [Sub-Tag1, Sub-Tag2]`

### View MCQs (Option 3):
```
3. 👀 View MCQs
```

**Display Format:**
```
📝 Question 1:
Q: What is a convolutional neural network?

🎯 Main Category: Technology
🏷️  Sub-Tags: Deep Learning, Computer Vision
📊 Difficulty: medium

   A. For images
   B. For text
   C. For audio
   D. None

✅ Correct Answer: A
💡 Explanation: CNNs process images
```

---

## 📈 Test Results

### Example Output:

**Q: "What is a convolutional neural network used for in deep learning?"**

| System | Main Tag | Sub-Tags |
|--------|----------|----------|
| **Keyword** | Technology | Deep Learning, Computer Vision |
| **LLM** | Technology | Artificial Intelligence, Machine Learning |

**Q: "What is the capital of France?"**

| System | Main Tag | Sub-Tags |
|--------|----------|----------|
| **Keyword** | General Knowledge | what, capital |
| **LLM** | Geography | Countries, Cities |

**Q: "What does backpropagation do in neural networks?"**

| System | Main Tag | Sub-Tags |
|--------|----------|----------|
| **Keyword** | Neural Networks | Optimization |
| **LLM** | Technology | Artificial Intelligence, Machine Learning |

---

## 🔧 Configuration

### Model Settings (.env):
```bash
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile  # ✅ Works great!
```

### Files Modified:
1. ✅ [question_tagger.py](question_tagger.py) - Hierarchical keyword tagging
2. ✅ [mcq_generator.py](mcq_generator.py) - Hierarchical LLM tagging
3. ✅ [terminal_app.py](terminal_app.py) - Enhanced display
4. ✅ [.env](.env) - Model configuration

---

## 📝 Data Structure

### Question Object (with hierarchical tags):
```json
{
  "question": "What is machine learning?",
  "options": {
    "A": "AI subset",
    "B": "Database",
    "C": "Network",
    "D": "OS"
  },
  "correct_answer": "A",
  "explanation": "ML is part of AI",

  "main_tag": "Technology",
  "sub_tags": ["Artificial Intelligence", "Machine Learning"],
  "tags": ["Technology", "Artificial Intelligence", "Machine Learning"],
  "category": "Technology",
  "difficulty": "medium",
  "bloom_category": "understand"
}
```

---

## 🎯 Best Practices

### When to use Keyword-Based:
- ✅ Technical AI/ML questions
- ✅ Offline tagging needed
- ✅ Fast batch processing
- ✅ No API costs

### When to use LLM-Based:
- ✅ General knowledge questions
- ✅ Mixed-domain content
- ✅ Need semantic understanding
- ✅ Higher accuracy required

### Hybrid Approach:
1. Use **LLM tagger** for initial tagging (option 7 in terminal app)
2. Use **manual tagging** (option 8) to fix any incorrect tags
3. Export results (option 5)

---

## 🧪 Testing

### Test Both Systems:
```bash
python test_hierarchical_both.py
```

### Test LLM Only:
```bash
python test_llm_now.py
```

### Run Terminal App:
```bash
python terminal_app.py
```

---

## 📊 Export Formats

All hierarchical tag fields are preserved when exporting:

### JSON Export (Option 5 → 1):
```json
{
  "mcqs": [
    {
      "question": "...",
      "main_tag": "Technology",
      "sub_tags": ["AI", "ML"],
      "tags": ["Technology", "AI", "ML"]
    }
  ]
}
```

### Excel Export (Option 5 → 4):
| Question | Main Tag | Sub-Tags | Tags | Difficulty |
|----------|----------|----------|------|------------|
| What is... | Technology | AI, ML | Technology, AI, ML | medium |

---

## ✅ Summary

**What You Have Now:**
1. ✅ Hierarchical tagging with 1 main + 2-3 sub-tags
2. ✅ Two tagging systems (keyword + LLM)
3. ✅ Automatic tagging in terminal app
4. ✅ Beautiful display of hierarchical tags
5. ✅ Full backward compatibility
6. ✅ Working with `llama-3.3-70b-versatile` model

**Next Steps:**
1. Run `python terminal_app.py`
2. Upload your MCQ file (option 7)
3. View tagged questions (option 3)
4. Export results (option 5)

🎉 **Enjoy your new hierarchical tagging system!**
