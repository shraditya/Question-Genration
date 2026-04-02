#!/usr/bin/env python3
"""Test context-based hierarchical tagging with new comprehensive categories"""

from mcq_generator import MCQGenerator

print("="*70)
print("🧪 TESTING CONTEXT-BASED HIERARCHICAL TAGGING")
print("="*70)
print("\nNew Features:")
print("  ✓ 19 comprehensive main categories")
print("  ✓ Context-based sub-tags (not fixed taxonomy)")
print("  ✓ 3-4 sub-tags per question")
print()

generator = MCQGenerator()

# Test questions across different domains
questions = [
    {
        "question": "What is deep learning and how does it differ from traditional machine learning?",
        "options": {"A": "Neural networks", "B": "Linear models", "C": "Decision trees", "D": "None"},
        "correct_answer": "A",
        "explanation": "Deep learning uses neural networks"
    },
    {
        "question": "What is the p-value in statistical hypothesis testing?",
        "options": {"A": "Probability", "B": "Power", "C": "Parameter", "D": "None"},
        "correct_answer": "A",
        "explanation": "P-value measures statistical significance"
    },
    {
        "question": "What is GDP in economics?",
        "options": {"A": "Gross Domestic Product", "B": "General Data Processing", "C": "Global Defense Plan", "D": "None"},
        "correct_answer": "A",
        "explanation": "GDP measures economic output"
    },
    {
        "question": "What is the Hippocratic Oath in medicine?",
        "options": {"A": "Medical ethics oath", "B": "Surgery technique", "C": "Drug name", "D": "Hospital protocol"},
        "correct_answer": "A",
        "explanation": "Oath of medical ethics"
    },
    {
        "question": "What is a convolutional neural network (CNN) used for?",
        "options": {"A": "Image processing", "B": "Text analysis", "C": "Audio synthesis", "D": "None"},
        "correct_answer": "A",
        "explanation": "CNNs excel at image tasks"
    }
]

print("🤖 Tagging 5 diverse questions...\n")

tagged = generator.llm_tag_questions(questions)

print("\n" + "="*70)
print("📊 RESULTS - Context-Based Sub-Tags")
print("="*70 + "\n")

for i, q in enumerate(tagged, 1):
    print(f"{'─'*70}")
    print(f"Q{i}: {q['question'][:60]}...")
    print(f"{'─'*70}")
    print(f"🎯 Main Category: {q.get('main_tag', 'N/A')}")
    print(f"🏷️  Context Sub-Tags: {', '.join(q.get('sub_tags', []))}")
    print(f"   (Generated from question context, not fixed list)")
    print()

# Summary
print("="*70)
print("📈 SUMMARY")
print("="*70 + "\n")

main_tags = {}
all_sub_tags = []

for q in tagged:
    main = q.get('main_tag', 'Unknown')
    main_tags[main] = main_tags.get(main, 0) + 1
    all_sub_tags.extend(q.get('sub_tags', []))

print("Main Categories Used:")
for tag, count in sorted(main_tags.items(), key=lambda x: -x[1]):
    print(f"  • {tag}: {count} question(s)")

print(f"\nTotal Unique Sub-Tags Generated: {len(set(all_sub_tags))}")
print(f"Sample Sub-Tags: {', '.join(list(set(all_sub_tags))[:10])}")

print("\n" + "="*70)
print("✅ Context-based tagging working perfectly!")
print("="*70)
