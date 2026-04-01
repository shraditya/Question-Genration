# MCQ Similarity Check System

This document explains how to check similarity between MCQs (Multiple Choice Questions) using our fine-tuned model.

## Overview

The similarity check system identifies duplicate or highly similar MCQs to ensure question uniqueness and quality. It uses a fine-tuned transformer model specifically trained on MCQ data.

## Fine-tuned Model

The fine-tuned similarity model has been uploaded to Google Drive for easy access:

**📦 Model Download Link:** [MCQ Similarity Fine-tuned Model on Google Drive](#)
> _Replace the link above with your actual Google Drive link_

## Files in this Branch

- **`mcq_similarity_colab.ipynb`**: Jupyter notebook for running similarity checks in Google Colab
- **`similiarty_data/`**: Contains test data and results
  - `duplicate_pairs.json`: Known duplicate MCQ pairs for validation
  - `test_results.json`: Similarity check results
  - `test.csv`: Test dataset

## How to Check MCQ Similarity

### Method 1: Using Google Colab (Recommended)

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

### Method 2: Local Setup

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
