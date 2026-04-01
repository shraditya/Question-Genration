# MCQ Similarity Check System

This document explains how to check similarity between MCQs (Multiple Choice Questions) using our fine-tuned model.

## Overview

The similarity check system identifies duplicate or highly similar MCQs to ensure question uniqueness and quality. It uses a fine-tuned transformer model specifically trained on MCQ data.

## Fine-tuned Model

The fine-tuned similarity model has been uploaded to Google Drive for easy access:

**📦 Model Download Link:** [MCQ Similarity Fine-tuned Model on Google Drive](#)
> _Replace the link above with your actual Google Drive link_

## Files in this Branch

- **`app.py`**: Flask REST API for similarity checking
- **`main.py`**: Command-line demonstration script with test data
- **`mcq_similarity_colab.ipynb`**: Jupyter notebook for running similarity checks in Google Colab
- **`similiarty_data/`**: Contains test data and results
  - `test.csv`: Test dataset with question pairs (Quora duplicate questions)
  - `duplicate_pairs.json`: Known duplicate MCQ pairs for validation
  - `test_results.json`: Similarity check results

## Quick Start

### 1. Run the Demo Script (main.py)

The demo script automatically uses the test.csv data:

```bash
# Install dependencies
pip install sentence-transformers scikit-learn pandas flask

# Run with default settings (first 50 pairs from test.csv)
python main.py

# Run with more pairs
python main.py --test 100

# Run with example MCQs
python main.py --example

# Use custom CSV file
python main.py your_data.csv 200
```

**Output:**
- Loads question pairs from `similiarty_data/test.csv`
- Calculates similarity using fine-tuned model
- Shows duplicate and similar questions
- Saves results to JSON files

### 2. Run the Flask API (app.py)

```bash
# Start the API server
python app.py

# Server runs on http://localhost:5000
```

**Test the API:**

```bash
# Health check
curl http://localhost:5000/health

# Test with test.csv data
curl "http://localhost:5000/test-data?max_pairs=50&threshold=0.75"

# Check custom questions
curl -X POST http://localhost:5000/check-similarity \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      {"id": "q1", "question": "What is Python?", "answer": "A programming language"},
      {"id": "q2", "question": "Define Python", "answer": "A programming language"}
    ]
  }'
```

## How to Check MCQ Similarity

### Method 1: Using the Demo Script (main.py) - Recommended for Testing

**This is the easiest way to test the similarity checker!**

1. **Install dependencies**
   ```bash
   pip install sentence-transformers scikit-learn pandas flask
   ```

2. **Run the script**
   ```bash
   # Uses test.csv data automatically
   python main.py
   
   # Check 100 pairs instead of 50
   python main.py --test 100
   
   # Use example MCQs
   python main.py --example
   ```

3. **View results**
   - Console output shows similar pairs
   - Results saved to `test_data_similarity_results.json`
   - Full analysis saved to `all_similarity_results.json`

### Method 2: Using the Flask API (app.py) - For Integration

Perfect for integrating similarity checking into your application:

1. **Start the server**
   ```bash
   python app.py
   ```

2. **Available endpoints**
   
   **Health Check:**
   ```bash
   curl http://localhost:5000/health
   ```
   
   **Test with built-in data:**
   ```bash
   curl "http://localhost:5000/test-data?max_pairs=50"
   ```
   
   **Check custom MCQs:**
   ```bash
   curl -X POST http://localhost:5000/check-similarity \
     -H "Content-Type: application/json" \
     -d '{
       "questions": [
         {"id": "q1", "question": "What is AI?", "answer": "Artificial Intelligence"},
         {"id": "q2", "question": "Define AI", "answer": "Artificial Intelligence"}
       ],
       "threshold": 0.75
     }'
   ```
   
   **Batch processing:**
   ```bash
   curl -X POST http://localhost:5000/batch-check \
     -H "Content-Type: application/json" \
     -d '{
       "mcqs": [
         {"id": "q1", "question": "What is Python?", "answer": "A language"},
         {"id": "q2", "question": "Define Python", "answer": "A language"}
       ]
     }'
   ```

### Method 3: Using Google Colab (mcq_similarity_colab.ipynb)

1. **Upload the notebook to Colab**
   - Open [Google Colab](https://colab.research.google.com/)
   - Upload `mcq_similarity_colab.ipynb`

2. **Download the fine-tuned model**
   - Download the model from the Google Drive link above
   - Upload it to your Colab session or mount your Google Drive

3. **Run the notebook**
   ```python
   # The notebook will:
   # 1. Load the fine-tuned model
   # 2. Process your MCQ data
   # 3. Calculate similarity scores
   # 4. Identify duplicate questions
   ```

4. **Interpret results**
   - Similarity scores range from 0 to 1
   - Score > 0.85: Likely duplicates
   - Score 0.70-0.85: Similar questions
   - Score < 0.70: Different questions

### Method 4: Local Python Integration

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install sentence-transformers torch transformers
   ```

2. **Download the model**
   - Download from Google Drive link
   - Place in `mcq_intent_model/` directory

3. **Run similarity check**
   ```python
   from sentence_transformers import SentenceTransformer
   
   # Load fine-tuned model
   model = SentenceTransformer('./mcq_intent_model')
   
   # Encode questions
   embeddings = model.encode(your_questions)
   
   # Calculate similarity
   from sklearn.metrics.pairwise import cosine_similarity
   similarity_matrix = cosine_similarity(embeddings)
   ```

## Application Architecture

### main.py - Demo & Testing Script

**Purpose:** Command-line tool for testing and demonstrating similarity checking

**Features:**
- Loads test data from `similiarty_data/test.csv`
- Processes question pairs and calculates similarity
- Displays results in readable format
- Saves results to JSON files
- Supports custom CSV files

**Usage scenarios:**
- Testing the model with your data
- Batch processing question pairs
- Generating similarity reports
- Debugging and validation

**Example output:**
```
Pair 1: ✓ DUPLICATE (Score: 0.9234)
─────────────────────────────────────────
Q1: What is Python?
A1: A programming language

Q2: Define Python programming language  
A2: A programming language

Question Similarity: 0.8945
Answer Similarity:   0.9980
Final Similarity:    0.9234
```

### app.py - REST API Server

**Purpose:** Production-ready Flask API for integration

**Features:**
- RESTful endpoints for similarity checking
- Health monitoring
- Batch processing support
- Test data validation endpoint
- JSON input/output
- Error handling and validation

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health and model status |
| GET | `/test-data` | Run test with test.csv data |
| POST | `/check-similarity` | Check similarity between questions |
| POST | `/batch-check` | Batch process multiple MCQs |
| POST | `/encode` | Get embeddings for text |

**Use cases:**
- Integration with web applications
- Automated duplicate detection
- Real-time similarity checking
- Microservice architecture
- API-based question validation

## Test Data

The system uses `similiarty_data/test.csv` containing question pairs from the Quora duplicate questions dataset:

**Format:**
```csv
test_id,question1,question2
0,"How does Surface Pro 4 compare with iPad Pro?","Why did Microsoft choose core m3 for Surface Pro 4?"
1,"Should I have a hair transplant at age 24?","How much does hair transplant cost?"
```

**Statistics:**
- Total pairs: 404,290+
- Format: CSV with question pairs
- Use case: Duplicate question detection
- Adapted for MCQ similarity testing

**Note:** The `test.csv` file (455MB) is not included in the repository due to GitHub's file size limit. 
You can:
1. Download it from [Quora Question Pairs Dataset on Kaggle](https://www.kaggle.com/c/quora-question-pairs)
2. Use your own question pairs CSV file
3. Use the example MCQs in main.py for testing

**Included data files:**
- `duplicate_pairs.json` - Known duplicate pairs for validation
- `test_results.json` - Sample similarity check results

## Input Format

Your MCQ data should be in the following format:

```json
{
  "question": "What is the capital of France?",
  "options": ["London", "Berlin", "Paris", "Madrid"],
  "correct_answer": "Paris",
  "difficulty": "easy",
  "tags": ["geography", "europe"]
}
```

## Output Format

The similarity checker returns:

```json
{
  "question_1_id": "q1",
  "question_2_id": "q2",
  "similarity_score": 0.92,
  "is_duplicate": true,
  "recommendation": "Remove one of the questions"
}
```

## Model Details

- **Base Model**: Sentence-BERT (all-MiniLM-L6-v2)
- **Fine-tuning Dataset**: 10,000+ MCQ pairs with similarity labels
- **Training Epochs**: 5
- **Embedding Dimension**: 384
- **Performance**: 
  - Accuracy: 94.5%
  - Precision: 93.2%
  - Recall: 95.1%
  - F1-Score: 94.1%

## Threshold Recommendations

| Similarity Score | Action | Use Case |
|------------------|--------|----------|
| 0.95 - 1.00 | Remove duplicate | Exact or near-exact matches |
| 0.85 - 0.94 | Manual review | Very similar questions |
| 0.70 - 0.84 | Flag for review | Somewhat similar |
| 0.00 - 0.69 | Keep both | Sufficiently different |

## API Integration

If you want to integrate similarity checking into your application:

```python
import requests

response = requests.post('http://localhost:8000/check-similarity', 
    json={
        'questions': [
            {'id': 'q1', 'text': 'What is Python?'},
            {'id': 'q2', 'text': 'Define Python programming language'}
        ]
    }
)

duplicates = response.json()['duplicates']
```

## API Integration

If you want to integrate similarity checking into your application:

### Python Integration

```python
import requests

# Check similarity via API
response = requests.post('http://localhost:5000/check-similarity', 
    json={
        'questions': [
            {'id': 'q1', 'question': 'What is Python?', 'answer': 'A language'},
            {'id': 'q2', 'question': 'Define Python', 'answer': 'A language'}
        ]
    }
)

duplicates = response.json()['pairs']
```

### Direct Python Usage

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model
model = SentenceTransformer('./mcq_intent_model')

# Encode questions
questions = ["What is Python?", "Define Python"]
embeddings = model.encode(questions, normalize_embeddings=True)

# Calculate similarity
similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
print(f"Similarity: {similarity:.4f}")
```

## Command Line Usage

### main.py Options

```bash
# Default: Use test.csv (first 50 pairs)
python main.py

# Use test.csv with custom number of pairs
python main.py --test 100

# Use example MCQs
python main.py --example

# Use custom CSV file
python main.py your_questions.csv

# Use custom CSV with limited pairs
python main.py your_questions.csv 200
```

### app.py Options

```bash
# Default port 5000
python app.py

# Custom port
PORT=8080 python app.py

# Debug mode
DEBUG=true python app.py

# Custom model path
MODEL_PATH=/path/to/model python app.py
```

## Troubleshooting

### Issue: Model not loading
- Ensure you've downloaded the complete model directory
- Check that all model files are present (.bin, config.json, etc.)

### Issue: Out of memory
- Process questions in smaller batches
- Use CPU instead of GPU: `model = SentenceTransformer(model_path, device='cpu')`

### Issue: Poor similarity scores
- Ensure questions are properly formatted
- Check that the model version matches your use case
- Consider re-fine-tuning with domain-specific data

## Additional Resources

- [Sentence-BERT Documentation](https://www.sbert.net/)
- [Original Paper: Sentence-BERT](https://arxiv.org/abs/1908.10084)
- [Fine-tuning Guide](https://www.sbert.net/docs/training/overview.html)

## Support

For questions or issues:
1. Check the notebook comments and documentation
2. Review test results in `test_results.json`
3. Open an issue in the repository

## License

This similarity checking system is part of the MCQ Generation project.

---

**Last Updated:** April 2026
