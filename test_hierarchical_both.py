#!/usr/bin/env python3
"""Test both keyword-based and LLM hierarchical tagging"""

from question_tagger import QuestionTagger
from mcq_generator import MCQGenerator

print("="*70)
print("🧪 TESTING HIERARCHICAL TAGGING - BOTH SYSTEMS")
print("="*70)

# Test questions
questions = [
    {
        "question": "What is a convolutional neural network used for in deep learning?",
        "options": {"A": "Images", "B": "Text", "C": "Audio", "D": "None"},
        "correct_answer": "A",
        "explanation": "CNNs are used for image processing"
    },
    {
        "question": "What is the capital of France?",
        "options": {"A": "Berlin", "B": "Paris", "C": "Rome", "D": "Madrid"},
        "correct_answer": "B",
        "explanation": "Paris is the capital"
    },
    {
        "question": "What does backpropagation do in neural networks?",
        "options": {"A": "Calculates gradients", "B": "Adds layers", "C": "Removes neurons", "D": "None"},
        "correct_answer": "A",
        "explanation": "Backpropagation computes gradients"
    }
]

print("\n" + "="*70)
print("1️⃣  KEYWORD-BASED HIERARCHICAL TAGGING")
print("="*70 + "\n")

tagger = QuestionTagger()
keyword_tagged = tagger.tag_questions(questions.copy())

for i, q in enumerate(keyword_tagged, 1):
    print(f"Q{i}: {q['question'][:50]}...")
    print(f"  🎯 Main: {q.get('main_tag', 'N/A')}")
    print(f"  🏷️  Subs: {', '.join(q.get('sub_tags', []))}")
    print(f"  📝 Tags: {q.get('tags', [])}")
    print()

print("="*70)
print("2️⃣  LLM-BASED HIERARCHICAL TAGGING")
print("="*70)

generator = MCQGenerator()
llm_tagged = generator.llm_tag_questions(questions.copy())

print("\n📊 RESULTS:")
for i, q in enumerate(llm_tagged, 1):
    print(f"\nQ{i}: {q['question'][:50]}...")
    print(f"  🎯 Main: {q.get('main_tag', 'N/A')}")
    print(f"  🏷️  Subs: {', '.join(q.get('sub_tags', []))}")
    print(f"  📝 Tags: {q.get('tags', [])}")

print("\n" + "="*70)
print("✅ BOTH SYSTEMS TESTED!")
print("="*70)

# Compare
print("\n📊 COMPARISON:")
print("-"*70)
for i in range(len(questions)):
    kw = keyword_tagged[i]
    llm = llm_tagged[i]
    print(f"\nQ{i+1}:")
    print(f"  Keyword: {kw.get('main_tag')} → {kw.get('sub_tags')}")
    print(f"  LLM:     {llm.get('main_tag')} → {llm.get('sub_tags')}")

print("\n✅ Test completed!")
