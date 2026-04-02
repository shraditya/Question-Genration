#!/usr/bin/env python3
"""Test fast batch tagging performance"""

from mcq_generator import MCQGenerator
import time

print("="*70)
print("⚡ FAST BATCH TAGGING TEST")
print("="*70)

generator = MCQGenerator()

# Create 20 test questions
questions = []
for i in range(20):
    questions.append({
        "question": f"What is concept {i+1} in computer science and machine learning?",
        "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
        "correct_answer": "A",
        "explanation": "Test question"
    })

print(f"\n📊 Testing with {len(questions)} questions...")
print(f"   Batch size: 10")
print(f"   Workers: 3 (parallel)")

start = time.time()

# Fast batch tagging
tagged = generator.llm_tag_questions(
    questions,
    batch_size=10,  # Process 10 at a time
    max_workers=3   # 3 parallel workers
)

elapsed = time.time() - start

print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
print(f"   Speed: {len(questions)/elapsed:.1f} questions/second")

# Show sample results
print(f"\n📊 Sample Results:")
for i in range(min(3, len(tagged))):
    q = tagged[i]
    print(f"\nQ{i+1}: {q['question'][:50]}...")
    print(f"  🎯 Main: {q.get('main_tag')}")
    print(f"  🏷️  Subs: {', '.join(q.get('sub_tags', []))}")

print(f"\n{'='*70}")
print(f"✅ Fast batch tagging complete!")
print(f"   104 questions would take ≈ {(104/len(questions)) * elapsed:.0f} seconds")
print(f"={'='*70}")
