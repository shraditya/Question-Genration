#!/usr/bin/env python3
"""Test current LLM tagging implementation"""

from mcq_generator import MCQGenerator

print("🧪 Testing Current LLM Tagging\n")

generator = MCQGenerator()
print(f"✅ Using model: {generator.model}\n")

# Just 2 simple questions
questions = [
    {
        "question": "What is machine learning?",
        "options": {"A": "AI", "B": "Database", "C": "Network", "D": "OS"},
        "correct_answer": "A",
        "explanation": "ML is part of AI"
    },
    {
        "question": "What is Paris?",
        "options": {"A": "Country", "B": "Capital of France", "C": "River", "D": "Mountain"},
        "correct_answer": "B",
        "explanation": "Paris is capital"
    }
]

print("📋 Tagging 2 questions with LLM...\n")

try:
    tagged = generator.llm_tag_questions(questions)

    print("\n" + "="*70)
    print("📊 RESULTS:")
    print("="*70 + "\n")

    for i, q in enumerate(tagged, 1):
        tags = q.get('tags', [])
        print(f"Q{i}: {q['question'][:50]}...")
        print(f"  Tags: {tags}")
        print()

    if any(q.get('tags') for q in tagged):
        print("✅ LLM TAGGING IS WORKING!")
    else:
        print("⚠️  No tags returned - LLM may have failed")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
