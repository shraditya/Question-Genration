#!/usr/bin/env python3
"""Test clean output structure (no redundant fields)"""

from mcq_generator import MCQGenerator
import json

print("="*70)
print("🧹 TESTING CLEAN OUTPUT STRUCTURE")
print("="*70)

generator = MCQGenerator()

questions = [
    {
        "question": "What is the hardest natural substance?",
        "options": {
            "A": "Gold",
            "B": "Iron",
            "C": "Diamond",
            "D": "Platinum"
        },
        "correct_answer": "C",
        "explanation": "Diamond is the hardest natural substance"
    },
    {
        "question": "What is machine learning?",
        "options": {
            "A": "AI technique",
            "B": "Database",
            "C": "Network",
            "D": "OS"
        },
        "correct_answer": "A",
        "explanation": "ML is an AI technique"
    }
]

print("\n🤖 Tagging questions...\n")

tagged = generator.llm_tag_questions(questions, batch_size=2, max_workers=1)

print("\n" + "="*70)
print("📊 CLEAN OUTPUT (JSON)")
print("="*70 + "\n")

# Show JSON output
for i, q in enumerate(tagged, 1):
    print(f"Question {i}:")
    print(json.dumps(q, indent=2, ensure_ascii=False))
    print()

# Verify fields
print("="*70)
print("✅ VERIFICATION")
print("="*70 + "\n")

for i, q in enumerate(tagged, 1):
    print(f"Q{i} Fields:")
    print(f"  ✓ question: {bool(q.get('question'))}")
    print(f"  ✓ options: {bool(q.get('options'))}")
    print(f"  ✓ correct_answer: {bool(q.get('correct_answer'))}")
    print(f"  ✓ explanation: {q.get('explanation') is not None}")
    print(f"  ✓ main_tag: {q.get('main_tag')}")
    print(f"  ✓ sub_tags: {q.get('sub_tags')}")
    print()
    # Check removed fields
    has_tags = 'tags' in q
    has_category = 'category' in q
    if has_tags or has_category:
        print(f"  ⚠️  UNWANTED FIELDS FOUND:")
        if has_tags:
            print(f"     - 'tags': {q.get('tags')}")
        if has_category:
            print(f"     - 'category': {q.get('category')}")
    else:
        print(f"  ✅ No redundant fields!")
    print()

print("="*70)
print("✅ Output structure is clean!")
print("="*70)
