"""
Flask API for MCQ Similarity Checking
Uses fine-tuned sentence-transformer model for intent-based similarity
"""

from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from itertools import combinations
import os

app = Flask(__name__)

# Configuration
MODEL_PATH = os.getenv('MODEL_PATH', './mcq_intent_model')
TEST_DATA_PATH = './similiarty_data/test.csv'
CUTOFF_THRESHOLD = 0.75  # Minimum similarity to report
DUPLICATE_THRESHOLD = 0.90  # Threshold for duplicate classification
HIGH_SIMILARITY_THRESHOLD = 0.80  # Threshold for high similarity

# Load model on startup
print(f"Loading model from {MODEL_PATH}...")
try:
    model = SentenceTransformer(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load model from {MODEL_PATH}: {e}")
    print("Using base model 'all-MiniLM-L6-v2' instead")
    model = SentenceTransformer('all-MiniLM-L6-v2')


def calculate_adaptive_similarity(q_sim, a_sim):
    """
    Adaptive answer weight formula:
    answer_weight = 0.15 + 0.70 × (1 − question_sim)
    
    - High q_sim → answer weight LOW (answer just confirms)
    - Low q_sim, but same answer → answer weight HIGH (answer reveals hidden concept match)
    """
    answer_weight = 0.15 + 0.70 * (1.0 - q_sim)
    question_weight = 1.0 - answer_weight
    final_sim = answer_weight * a_sim + question_weight * q_sim
    return final_sim, answer_weight


def classify_similarity(sim_score):
    """Classify similarity score into categories"""
    if sim_score >= DUPLICATE_THRESHOLD:
        return 'Duplicate'
    elif sim_score >= HIGH_SIMILARITY_THRESHOLD:
        return 'Highly Similar'
    elif sim_score >= CUTOFF_THRESHOLD:
        return 'Similar'
    else:
        return 'Different'


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'model_path': MODEL_PATH
    })


@app.route('/check-similarity', methods=['POST'])
def check_similarity():
    """
    Check similarity between MCQs
    
    Request body:
    {
        "questions": [
            {
                "id": "q1",
                "question": "What is Python?",
                "answer": "A programming language"
            },
            {
                "id": "q2", 
                "question": "Define Python",
                "answer": "A programming language"
            }
        ],
        "threshold": 0.75  # optional, default 0.75
    }
    
    Response:
    {
        "total_pairs": 1,
        "similar_pairs": 1,
        "duplicates": 1,
        "pairs": [
            {
                "q1_id": "q1",
                "q2_id": "q2",
                "question_similarity": 0.95,
                "answer_similarity": 1.0,
                "final_similarity": 0.97,
                "label": "Duplicate",
                "recommendation": "Remove one question"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'questions' not in data:
            return jsonify({'error': 'Missing "questions" field in request'}), 400
        
        questions = data['questions']
        threshold = data.get('threshold', CUTOFF_THRESHOLD)
        
        if len(questions) < 2:
            return jsonify({'error': 'At least 2 questions required'}), 400
        
        # Validate question format
        for i, q in enumerate(questions):
            if 'question' not in q or 'answer' not in q:
                return jsonify({'error': f'Question {i} missing "question" or "answer" field'}), 400
            if 'id' not in q:
                q['id'] = f'q{i}'
        
        # Encode questions and answers
        question_texts = [q['question'] for q in questions]
        answer_texts = [q['answer'] for q in questions]
        
        q_embs = model.encode(question_texts, batch_size=128, normalize_embeddings=True)
        a_embs = model.encode(answer_texts, batch_size=128, normalize_embeddings=True)
        
        # Calculate similarity matrices
        q_mat = cosine_similarity(q_embs, q_embs)
        a_mat = cosine_similarity(a_embs, a_embs)
        
        # Find similar pairs
        results = []
        n = len(questions)
        
        for i, j in combinations(range(n), 2):
            q_sim = float(q_mat[i][j])
            a_sim = float(a_mat[i][j])
            final_sim, answer_weight = calculate_adaptive_similarity(q_sim, a_sim)
            
            if final_sim < threshold:
                continue
            
            label = classify_similarity(final_sim)
            
            # Recommendation based on similarity
            if final_sim >= DUPLICATE_THRESHOLD:
                recommendation = "Remove one question - likely duplicate"
            elif final_sim >= HIGH_SIMILARITY_THRESHOLD:
                recommendation = "Review manually - highly similar"
            else:
                recommendation = "Flag for review - somewhat similar"
            
            results.append({
                'q1_id': questions[i]['id'],
                'q2_id': questions[j]['id'],
                'q1_text': questions[i]['question'],
                'q2_text': questions[j]['question'],
                'q1_answer': questions[i]['answer'],
                'q2_answer': questions[j]['answer'],
                'question_similarity': round(q_sim, 4),
                'answer_similarity': round(a_sim, 4),
                'answer_weight': round(answer_weight, 4),
                'final_similarity': round(final_sim, 4),
                'label': label,
                'recommendation': recommendation
            })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x['final_similarity'], reverse=True)
        
        # Summary statistics
        duplicates = sum(1 for r in results if r['label'] == 'Duplicate')
        highly_similar = sum(1 for r in results if r['label'] == 'Highly Similar')
        
        return jsonify({
            'success': True,
            'total_questions': len(questions),
            'total_pairs_checked': n * (n - 1) // 2,
            'similar_pairs_found': len(results),
            'duplicates': duplicates,
            'highly_similar': highly_similar,
            'threshold_used': threshold,
            'pairs': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/batch-check', methods=['POST'])
def batch_check():
    """
    Check similarity for a batch of MCQs from a CSV or JSON
    
    Request body:
    {
        "mcqs": [
            {
                "id": "q1",
                "question": "What is Python?",
                "options": ["A", "B", "C", "D"],
                "answer": "A programming language",
                "answer_idx": 0
            },
            ...
        ],
        "threshold": 0.75,
        "return_full_matrix": false  # optional
    }
    """
    try:
        data = request.get_json()
        mcqs = data.get('mcqs', [])
        threshold = data.get('threshold', CUTOFF_THRESHOLD)
        return_matrix = data.get('return_full_matrix', False)
        
        if len(mcqs) < 2:
            return jsonify({'error': 'At least 2 MCQs required'}), 400
        
        # Extract questions and answers
        questions = [m.get('question', '') for m in mcqs]
        answers = [m.get('answer', '') for m in mcqs]
        
        # Encode
        q_embs = model.encode(questions, batch_size=128, normalize_embeddings=True)
        a_embs = model.encode(answers, batch_size=128, normalize_embeddings=True)
        
        # Similarity matrices
        q_mat = cosine_similarity(q_embs, q_embs)
        a_mat = cosine_similarity(a_embs, a_embs)
        
        # Calculate adaptive similarity for all pairs
        n = len(mcqs)
        final_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    final_matrix[i][j] = 1.0
                else:
                    q_sim = q_mat[i][j]
                    a_sim = a_mat[i][j]
                    final_sim, _ = calculate_adaptive_similarity(q_sim, a_sim)
                    final_matrix[i][j] = final_sim
        
        # Find duplicates
        duplicates = []
        for i, j in combinations(range(n), 2):
            if final_matrix[i][j] >= threshold:
                duplicates.append({
                    'id1': mcqs[i].get('id', f'q{i}'),
                    'id2': mcqs[j].get('id', f'q{j}'),
                    'similarity': round(final_matrix[i][j], 4),
                    'label': classify_similarity(final_matrix[i][j])
                })
        
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
        result = {
            'success': True,
            'total_mcqs': n,
            'duplicates_found': len(duplicates),
            'duplicates': duplicates
        }
        
        if return_matrix:
            result['similarity_matrix'] = final_matrix.tolist()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/encode', methods=['POST'])
def encode():
    """
    Encode text into embeddings
    
    Request body:
    {
        "texts": ["Text 1", "Text 2", ...]
    }
    
    Response:
    {
        "embeddings": [[...], [...], ...]
    }
    """
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts:
            return jsonify({'error': 'No texts provided'}), 400
        
        embeddings = model.encode(texts, batch_size=128, normalize_embeddings=True)
        
        return jsonify({
            'success': True,
            'count': len(texts),
            'embedding_dim': embeddings.shape[1],
            'embeddings': embeddings.tolist()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.route('/test-data', methods=['GET'])
def test_with_data():
    """
    Run similarity check on test.csv data
    
    Query params:
    - max_pairs: Maximum number of pairs to check (default: 50)
    - threshold: Similarity threshold (default: 0.75)
    """
    try:
        import pandas as pd
        
        max_pairs = request.args.get('max_pairs', 50, type=int)
        threshold = request.args.get('threshold', CUTOFF_THRESHOLD, type=float)
        
        # Load test data
        df = pd.read_csv(TEST_DATA_PATH)
        
        if max_pairs and len(df) > max_pairs:
            df = df.head(max_pairs)
        
        # Convert to question pairs
        pairs = []
        for idx, row in df.iterrows():
            q1 = str(row.get('question1', '')).strip()
            q2 = str(row.get('question2', '')).strip()
            
            if q1 and q2:
                pairs.append({
                    'id': f'pair_{idx}',
                    'question1': q1,
                    'question2': q2
                })
        
        # Encode all questions
        all_questions = []
        pair_indices = []
        for pair in pairs:
            pair_indices.append((len(all_questions), len(all_questions) + 1))
            all_questions.append(pair['question1'])
            all_questions.append(pair['question2'])
        
        # Encode questions
        q_embs = model.encode(all_questions, batch_size=128, normalize_embeddings=True)
        
        # Calculate similarities for each pair
        results = []
        for i, (idx1, idx2) in enumerate(pair_indices):
            from sklearn.metrics.pairwise import cosine_similarity
            sim = float(cosine_similarity([q_embs[idx1]], [q_embs[idx2]])[0][0])
            
            if sim >= threshold:
                label = classify_similarity(sim)
                results.append({
                    'pair_id': pairs[i]['id'],
                    'question1': pairs[i]['question1'],
                    'question2': pairs[i]['question2'],
                    'similarity': round(sim, 4),
                    'label': label
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return jsonify({
            'success': True,
            'total_pairs_checked': len(pairs),
            'similar_pairs_found': len(results),
            'duplicates': sum(1 for r in results if r['label'] == 'Duplicate'),
            'threshold_used': threshold,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*60}")
    print(f"MCQ Similarity Check API")
    print(f"{'='*60}")
    print(f"Model: {MODEL_PATH}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"\nAvailable endpoints:")
    print(f"  GET  /health           - Health check")
    print(f"  GET  /test-data        - Run test with test.csv data")
    print(f"  POST /check-similarity - Check similarity between MCQs")
    print(f"  POST /batch-check      - Batch check for duplicates")
    print(f"  POST /encode           - Encode texts to embeddings")
    print(f"{'='*60}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
