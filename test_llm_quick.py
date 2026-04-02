#!/usr/bin/env python3
"""Quick test to verify LLM is working with llama-3.3-70b-versatile"""

from mcq_generator import MCQGenerator

print("🧪 Testing LLM with llama-3.3-70b-versatile model\n")

generator = MCQGenerator()
print(f"✅ Model loaded: {generator.model}\n")

# Test with 3 questions
questions = [
    {
        "question": "What is a convolutional neural network?",
        "options": {"A": "For images", "B": "For text", "C": "For audio", "D": "None"},
        "correct_answer": "A",
        "explanation": "CNNs process images"
    },
    {
        "question": "What is the capital of France?",
        "options": {"A": "Berlin", "B": "Paris", "C": "Rome", "D": "Madrid"},
        "correct_answer": "B",
        "explanation": "Paris"
    },
    {
        "question": "What does AI stand for?",
        "options": {"A": "Artificial Intelligence", "B": "Auto Input", "C": "Advanced Interface", "D": "None"},
        "correct_answer": "A",
        "explanation": "AI"
    }
]

print("📋 Tagging 3 questions...\n")
tagged = generator.llm_tag_questions(questions, batch_size=3, max_workers=1)

print("\n" + "="*70)
print("📊 RESULTS:")
print("="*70 + "\n")

success = True
for i, q in enumerate(tagged, 1):
    main_tag = q.get('main_tag', 'FAILED')
    sub_tags = q.get('sub_tags', [])

    if main_tag != 'General Knowledge' or (sub_tags and sub_tags[0] != 'General'):
        print(f"✅ Q{i}: {main_tag} → {sub_tags}")
    else:
        print(f"⚠️  Q{i}: {main_tag} → {sub_tags} (fallback)")
        success = False

if success:
    print("\n" + "="*70)
    print("✅ LLM IS WORKING PERFECTLY!")
    print("="*70)
else:
    print("\n" + "="*70)
    print("⚠️  LLM returned fallback values - check if API is working")
    print("="*70)
