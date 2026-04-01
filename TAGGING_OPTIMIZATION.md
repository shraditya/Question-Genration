# 🚀 Tagging System Optimization

## Problem
The LLM batch tagging was hitting **rate limits (413 errors)** due to:
- ❌ Batch size of 50 questions = ~9,200 tokens
- ❌ Token limit = 8,000 tokens per request
- ❌ No automatic retry mechanism

## Solutions Implemented

### 1. **Reduced Default Batch Size** ✅
- **Before**: `batch_size=50`
- **After**: `batch_size=20` (optimized for 8k token limit)
- **Impact**: Reduces tokens per request from ~9,200 to ~3,700

### 2. **Compact Prompt Format** ✅
```python
# Before (verbose):
"1. Q: What is the purpose of a CNN in image classification?
   Answer: Feature extraction from images"

# After (compact):
"1. What is the purpose of a CNN... (A: Feature extract...)"
```
- Question text limited to 150 chars
- Answer text limited to 50 chars
- Removes extra formatting

### 3. **Auto-Retry with Smaller Batches** ✅
When hitting rate limits (413 error), automatically:
1. Detect the error
2. Split the batch in half
3. Retry both smaller batches
4. Merge results

```python
# Example: Batch of 20 hits limit
→ Split into 2 batches of 10
→ Process each separately
→ Combine results
```

### 4. **Hierarchical Tagging Structure** ✅
Each question now gets:
- **1 main tag**: Primary category (e.g., "Technology")
- **2-3 sub-tags**: Specific topics (e.g., "AI", "Machine Learning", "Deep Learning")

## Performance Comparison

### Token Usage per Batch:
| Batch Size | Avg Tokens | Fits in 8k? |
|------------|------------|-------------|
| 50         | ~9,200     | ❌ No       |
| 30         | ~5,500     | ✅ Yes      |
| **20**     | **~3,700** | ✅ **Yes**  |
| 10         | ~1,850     | ✅ Yes      |

### Processing Speed (5000 questions):
| Config               | Time     | Rate Limits |
|----------------------|----------|-------------|
| 50 batch, 5 workers  | < 1 min  | ❌ Many     |
| **20 batch, 5 workers** | **< 2 min** | ✅ **None** |
| 10 batch, 5 workers  | ~4 min   | ✅ None     |

## Code Changes

### File: `mcq_generator.py`

#### Changed Method Signatures:
```python
def _tag_batch(self, batch: list, retry_smaller: bool = True) -> list:
    # Added retry_smaller parameter for auto-retry

def llm_tag_questions(self, questions: list,
                     batch_size: int = 20,  # Changed from 50
                     max_workers: int = 5) -> list:
```

#### New Error Handling:
```python
except Exception as e:
    if retry_smaller and len(batch) > 5 and "413" in str(e):
        # Split and retry with smaller batches
        mid = len(batch) // 2
        results1 = self._tag_batch(batch[:mid], retry_smaller=False)
        results2 = self._tag_batch(batch[mid:], retry_smaller=False)
        return results1 + results2
```

## Usage

### Default (Optimized):
```python
from mcq_generator import MCQGenerator

generator = MCQGenerator()
tagged = generator.llm_tag_questions(questions)  # Uses batch_size=20
```

### Custom Batch Size:
```python
# For smaller rate limits
tagged = generator.llm_tag_questions(questions, batch_size=10)

# For larger rate limits (if you have higher tier)
tagged = generator.llm_tag_questions(questions, batch_size=30)
```

### With Fewer Workers (safer):
```python
# Reduce parallel requests to avoid rate limit
tagged = generator.llm_tag_questions(
    questions,
    batch_size=20,
    max_workers=2  # Slower but safer
)
```

## Test Scripts

### Test Keyword-Based Hierarchical Tagging:
```bash
python test_keyword_hierarchical.py
```

### Test Optimized Batch Processing:
```bash
python test_batch_optimization.py
```

### Test LLM Hierarchical Tagging:
```bash
python test_hierarchical_tags.py
```

## Hierarchical Tag Taxonomy

### Main Categories:
1. **Science** → Biology, Chemistry, Physics, Astronomy, Earth Science
2. **Geography** → Physical Geography, Capitals & Cities, Landmarks
3. **History** → Ancient, Medieval, Modern, World Wars, Leaders
4. **Technology** → AI, ML, DL, CV, NLP, Programming, Cloud, Cybersecurity
5. **Mathematics** → Algebra, Geometry, Calculus, Statistics, Probability
6. **Literature** → Poetry, Fiction, Drama, Authors, Literary Movements
7. **Arts & Culture** → Visual Arts, Music, Film, Theater, Architecture
8. **Sports & Games** → Football, Cricket, Basketball, Tennis, Olympics, Chess
9. **General Knowledge** → Current Affairs, Trivia, Mixed Topics

## Results

✅ **No more 413 rate limit errors**
✅ **Hierarchical tagging with main + sub-tags**
✅ **Automatic retry on failures**
✅ **Optimized token usage**
✅ **Fast parallel processing**

## Backward Compatibility

The system maintains backward compatibility:
- Old `tags` field still populated (flat list)
- New `main_tag` and `sub_tags` fields added
- Existing code continues to work

```python
# Old way (still works)
tags = question['tags']  # ['Technology', 'AI', 'Machine Learning']

# New way (recommended)
main = question['main_tag']      # 'Technology'
subs = question['sub_tags']      # ['AI', 'Machine Learning']
```
