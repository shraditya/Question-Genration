"""
MCQ Similarity Check - Main Demonstration Script

This script demonstrates how the MCQ similarity checking system works.
It shows:
1. Loading the fine-tuned model
2. Encoding questions and answers
3. Calculating adaptive similarity
4. Finding duplicates and similar questions
"""

import json
import os
from itertools import combinations
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration
MODEL_PATH = os.getenv('MODEL_PATH', './mcq_intent_model')
TEST_DATA_PATH = './similiarty_data/test.csv'
CUTOFF_THRESHOLD = 0.75  # Minimum similarity to report
DUPLICATE_THRESHOLD = 0.90  # Threshold for duplicate classification
HIGH_SIMILARITY_THRESHOLD = 0.80  # Threshold for high similarity


def load_model():
    """Load the fine-tuned similarity model"""
    print(f"Loading model from {MODEL_PATH}...")
    try:
        model = SentenceTransformer(MODEL_PATH)
        print("✓ Fine-tuned model loaded successfully!")
        return model
    except Exception as e:
        print(f"⚠ Warning: Could not load model from {MODEL_PATH}: {e}")
        print("  Using base model 'all-MiniLM-L6-v2' instead")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model


def calculate_adaptive_similarity(q_sim, a_sim):
    """
    Adaptive answer weight formula:
    answer_weight = 0.15 + 0.70 × (1 − question_sim)
    
    Explanation:
    - High q_sim → answer weight LOW (answer just confirms)
    - Low q_sim, but same answer → answer weight HIGH (answer reveals hidden concept match)
    - This ensures that questions with similar intent but different wording are detected
    
    Args:
        q_sim: Question cosine similarity (0-1)
        a_sim: Answer cosine similarity (0-1)
    
    Returns:
        final_sim: Weighted final similarity score
        answer_weight: The calculated answer weight used
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


def find_similar_mcqs(mcqs, model, threshold=CUTOFF_THRESHOLD, verbose=True):
    """
    Find similar MCQs using the fine-tuned model
    
    Args:
        mcqs: List of MCQ dictionaries with 'question' and 'answer' keys
        model: SentenceTransformer model
        threshold: Minimum similarity threshold to report
        verbose: Print detailed information
    
    Returns:
        List of similar pairs with similarity scores
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"Checking {len(mcqs)} MCQs for similarity...")
        print(f"Threshold: {threshold}")
        print(f"{'='*70}\n")
    
    # Extract questions and answers
    questions = [m['question'] for m in mcqs]
    answers = [m['answer'] for m in mcqs]
    
    # Encode questions and answers
    if verbose:
        print("📝 Encoding questions...")
    q_embs = model.encode(questions, batch_size=128, show_progress_bar=verbose, 
                          normalize_embeddings=True)
    
    if verbose:
        print("📝 Encoding answers...")
    a_embs = model.encode(answers, batch_size=128, show_progress_bar=verbose, 
                          normalize_embeddings=True)
    
    # Calculate similarity matrices
    if verbose:
        print("🔍 Calculating similarity matrices...")
    q_mat = cosine_similarity(q_embs, q_embs)
    a_mat = cosine_similarity(a_embs, a_embs)
    
    if verbose:
        print(f"Matrix shape: {q_mat.shape}\n")
    
    # Find similar pairs
    results = []
    n = len(mcqs)
    
    for i, j in combinations(range(n), 2):
        q_sim = float(q_mat[i][j])
        a_sim = float(a_mat[i][j])
        final_sim, answer_weight = calculate_adaptive_similarity(q_sim, a_sim)
        
        if final_sim < threshold:
            continue
        
        label = classify_similarity(final_sim)
        
        results.append({
            'idx1': i,
            'idx2': j,
            'q1': mcqs[i]['question'],
            'a1': mcqs[i]['answer'],
            'q2': mcqs[j]['question'],
            'a2': mcqs[j]['answer'],
            'question_sim': round(q_sim, 4),
            'answer_sim': round(a_sim, 4),
            'answer_weight': round(answer_weight, 4),
            'final_sim': round(final_sim, 4),
            'label': label,
        })
    
    # Sort by similarity (highest first)
    results.sort(key=lambda x: x['final_sim'], reverse=True)
    
    if verbose:
        duplicates = sum(1 for r in results if r['label'] == 'Duplicate')
        highly_similar = sum(1 for r in results if r['label'] == 'Highly Similar')
        similar = sum(1 for r in results if r['label'] == 'Similar')
        
        print(f"✓ Found {len(results)} similar pairs above threshold {threshold}")
        print(f"  • Duplicates: {duplicates}")
        print(f"  • Highly Similar: {highly_similar}")
        print(f"  • Similar: {similar}")
        print()
    
    return results


def print_results(results, max_display=10):
    """Print similarity results in a readable format"""
    print(f"\n{'='*70}")
    print("SIMILARITY CHECK RESULTS")
    print(f"{'='*70}\n")
    
    for i, result in enumerate(results[:max_display], 1):
        print(f"Pair #{i}: {result['label']} (Score: {result['final_sim']})")
        print(f"{'─'*70}")
        print(f"Q1: {result['q1']}")
        print(f"A1: {result['a1']}")
        print()
        print(f"Q2: {result['q2']}")
        print(f"A2: {result['a2']}")
        print()
        print(f"Question Similarity: {result['question_sim']:.4f}")
        print(f"Answer Similarity:   {result['answer_sim']:.4f}")
        print(f"Answer Weight:       {result['answer_weight']:.4f}")
        print(f"Final Similarity:    {result['final_sim']:.4f}")
        print(f"{'='*70}\n")
    
    if len(results) > max_display:
        print(f"... and {len(results) - max_display} more pairs\n")


def save_results(results, output_file='similarity_results.json'):
    """Save results to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Results saved to {output_file}")


def example_usage():
    """Demonstrate the similarity checking system with example MCQs"""
    
    # Example MCQs for testing
    example_mcqs = [
        {
            "id": "q1",
            "question": "What is Python?",
            "answer": "A high-level programming language",
            "options": ["A language", "A snake", "A tool", "A framework"]
        },
        {
            "id": "q2",
            "question": "Define Python programming language",
            "answer": "A high-level programming language",
            "options": ["A language", "A snake", "A tool", "A framework"]
        },
        {
            "id": "q3",
            "question": "What is machine learning?",
            "answer": "A subset of AI that learns from data",
            "options": ["AI subset", "Programming", "Database", "Network"]
        },
        {
            "id": "q4",
            "question": "Explain machine learning",
            "answer": "AI technique that learns from data",
            "options": ["AI subset", "Programming", "Database", "Network"]
        },
        {
            "id": "q5",
            "question": "What is JavaScript?",
            "answer": "A scripting language for web development",
            "options": ["Web language", "Coffee", "Framework", "Database"]
        },
        {
            "id": "q6",
            "question": "What is the capital of France?",
            "answer": "Paris",
            "options": ["London", "Paris", "Berlin", "Madrid"]
        },
        {
            "id": "q7",
            "question": "Name the capital city of France",
            "answer": "Paris",
            "options": ["London", "Paris", "Berlin", "Madrid"]
        },
    ]
    
    # Load model
    model = load_model()
    
    # Find similar MCQs
    results = find_similar_mcqs(example_mcqs, model, threshold=0.75)
    
    # Print results
    print_results(results, max_display=5)
    
    # Save to file
    save_results(results, 'example_similarity_results.json')
    
    # Demonstrate how to use specific pairs
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70 + "\n")
    
    for result in results[:3]:
        if result['final_sim'] >= DUPLICATE_THRESHOLD:
            print(f"⚠ DUPLICATE DETECTED: Remove one of these questions")
            print(f"   Q1 (ID: {example_mcqs[result['idx1']]['id']})")
            print(f"   Q2 (ID: {example_mcqs[result['idx2']]['id']})")
            print(f"   Similarity: {result['final_sim']:.4f}\n")
        elif result['final_sim'] >= HIGH_SIMILARITY_THRESHOLD:
            print(f"⚠ HIGH SIMILARITY: Manual review recommended")
            print(f"   Q1 (ID: {example_mcqs[result['idx1']]['id']})")
            print(f"   Q2 (ID: {example_mcqs[result['idx2']]['id']})")
            print(f"   Similarity: {result['final_sim']:.4f}\n")


def load_and_check_test_data(csv_file=TEST_DATA_PATH, max_pairs=100):
    """Load question pairs from test CSV and check for duplicates"""
    import pandas as pd
    
    print(f"Loading test data from {csv_file}...")
    df = pd.read_csv(csv_file)
    
    print(f"Total pairs in dataset: {len(df)}")
    
    if max_pairs and len(df) > max_pairs:
        print(f"Using first {max_pairs} pairs for testing...\n")
        df = df.head(max_pairs)
    
    # Convert question pairs to MCQ format
    # Each pair becomes two separate MCQs that we'll compare
    mcqs = []
    pair_indices = []
    
    for idx, row in df.iterrows():
        q1 = str(row.get('question1', '')).strip()
        q2 = str(row.get('question2', '')).strip()
        
        if not q1 or not q2:
            continue
        
        # Add both questions (using question text as answer for pair comparison)
        mcqs.append({
            'question': q1,
            'answer': q1,  # For pairs, we compare questions primarily
            'original_idx': idx,
            'pair_position': 1
        })
        mcqs.append({
            'question': q2,
            'answer': q2,
            'original_idx': idx,
            'pair_position': 2
        })
        pair_indices.append((len(mcqs) - 2, len(mcqs) - 1))
    
    print(f"✓ Loaded {len(pair_indices)} question pairs ({len(mcqs)} total questions)\n")
    
    model = load_model()
    
    # Check all questions against each other
    all_results = find_similar_mcqs(mcqs, model, threshold=0.65, verbose=True)
    
    # Extract results for the original pairs
    print(f"\n{'='*70}")
    print("CHECKING ORIGINAL QUESTION PAIRS")
    print(f"{'='*70}\n")
    
    pair_results = []
    for pair_idx, (idx1, idx2) in enumerate(pair_indices):
        # Find similarity between the pair
        q_sim = None
        for result in all_results:
            if (result['idx1'] == idx1 and result['idx2'] == idx2) or \
               (result['idx1'] == idx2 and result['idx2'] == idx1):
                q_sim = result['final_sim']
                pair_results.append({
                    'pair_id': pair_idx,
                    'question1': mcqs[idx1]['question'],
                    'question2': mcqs[idx2]['question'],
                    'similarity': result['final_sim'],
                    'label': result['label']
                })
                break
        
        if q_sim:
            status = "✓ DUPLICATE" if q_sim >= DUPLICATE_THRESHOLD else \
                    "⚠ SIMILAR" if q_sim >= HIGH_SIMILARITY_THRESHOLD else "• Similar"
            print(f"Pair {pair_idx + 1}: {status} (Score: {q_sim:.4f})")
    
    print(f"\n✓ Analyzed {len(pair_results)} pairs")
    print(f"  Duplicates: {sum(1 for p in pair_results if p['similarity'] >= DUPLICATE_THRESHOLD)}")
    print(f"  Highly Similar: {sum(1 for p in pair_results if HIGH_SIMILARITY_THRESHOLD <= p['similarity'] < DUPLICATE_THRESHOLD)}")
    print(f"  Similar: {sum(1 for p in pair_results if CUTOFF_THRESHOLD <= p['similarity'] < HIGH_SIMILARITY_THRESHOLD)}")
    
    # Print detailed results
    print_results(all_results[:10], max_display=5)
    
    # Save results
    save_results(pair_results, 'test_data_similarity_results.json')
    save_results(all_results, 'all_similarity_results.json')
    
    return pair_results, all_results


if __name__ == '__main__':
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║       MCQ SIMILARITY CHECK - Demonstration Script                ║
║                                                                  ║
║  This script demonstrates how the similarity checking works      ║
║  using adaptive weighted similarity (question + answer)          ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--example':
            # Run example usage
            example_usage()
        elif sys.argv[1] == '--test':
            # Run with test data
            max_pairs = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            load_and_check_test_data(TEST_DATA_PATH, max_pairs=max_pairs)
        else:
            # Load from custom CSV file
            csv_file = sys.argv[1]
            max_pairs = int(sys.argv[2]) if len(sys.argv) > 2 else None
            load_and_check_test_data(csv_file, max_pairs=max_pairs)
    else:
        # Default: Run with test data
        print("Running with test data from similiarty_data/test.csv...")
        print("(Use --example for example MCQs, or provide custom CSV path)\n")
        load_and_check_test_data(TEST_DATA_PATH, max_pairs=50)
    
    print("\n" + "="*70)
    print("Usage:")
    print("  python main.py                    # Use test.csv (first 50 pairs)")
    print("  python main.py --test 100         # Use test.csv (first 100 pairs)")
    print("  python main.py --example          # Use example MCQs")
    print("  python main.py custom.csv         # Use custom CSV file")
    print("  python main.py custom.csv 200     # Use custom CSV (first 200 pairs)")
    print("\nFor API usage: python app.py")
    print("="*70 + "\n")
