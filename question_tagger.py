import re
from typing import List, Dict, Any, Optional
from collections import Counter


class QuestionTagger:
    """
    Question tagging system.

    Analysis is restricted to:
      - The question text
      - The correct answer option text only

    When the system cannot confidently determine tags (low confidence),
    it falls back to interactive user input.
    """

    # Below this score the system considers itself "unsure"
    CONFIDENCE_THRESHOLD = 1.5

    def __init__(self):
        # Topic keywords mapping
        self.topic_keywords = {
            "machine_learning": [
                "machine learning", "ml", "model", "training", "prediction", "algorithm",
                "supervised", "unsupervised", "classification", "regression", "clustering",
                "neural network", "deep learning", "feature", "label", "dataset"
            ],
            "transformer_architecture": [
                "transformer", "attention", "encoder", "decoder", "self-attention",
                "multi-head", "positional encoding", "feed-forward", "layer normalization",
                "residual connection", "skip connection"
            ],
            "natural_language_processing": [
                "nlp", "natural language", "text", "sentence", "token", "embedding",
                "word2vec", "bert", "language model", "sequence", "translation",
                "summarization", "sentiment"
            ],
            "computer_vision": [
                "image", "vision", "cnn", "convolutional", "pixel", "visual",
                "object detection", "segmentation", "classification", "resnet"
            ],
            "data_preprocessing": [
                "preprocessing", "normalization", "standardization", "cleaning",
                "feature engineering", "data preparation", "scaling", "encoding"
            ],
            "evaluation_metrics": [
                "accuracy", "precision", "recall", "f1", "loss", "metric", "evaluate",
                "validation", "test set", "confusion matrix", "roc", "auc"
            ],
            "optimization": [
                "optimizer", "gradient descent", "adam", "sgd", "learning rate",
                "backpropagation", "convergence", "minimize", "maximize"
            ],
            "attention_mechanism": [
                "attention", "query", "key", "value", "attention weights", "scaled dot-product",
                "attention score", "context vector"
            ],
            "sequence_modeling": [
                "sequence", "rnn", "lstm", "gru", "recurrent", "time step",
                "vanishing gradient", "long short-term"
            ],
            "training_techniques": [
                "batch", "epoch", "iteration", "dropout", "regularization", "overfitting",
                "underfitting", "early stopping", "data augmentation"
            ]
        }

        # Difficulty indicators
        self.difficulty_indicators = {
            "easy": [
                "what is", "define", "list", "name", "which", "identify",
                "basic", "simple", "primary", "main"
            ],
            "medium": [
                "how does", "explain", "describe", "compare", "contrast",
                "why does", "what happens", "purpose", "function"
            ],
            "hard": [
                "analyze", "evaluate", "critique", "justify", "design",
                "implement", "optimize", "trade-off", "limitation", "complexity",
                "mathematical", "calculate", "derive"
            ]
        }

        # Bloom's taxonomy categories
        self.bloom_categories = {
            "remember":   ["define", "list", "recall", "name", "state", "identify"],
            "understand": ["explain", "describe", "summarize", "paraphrase", "interpret"],
            "apply":      ["apply", "use", "demonstrate", "solve", "implement"],
            "analyze":    ["analyze", "compare", "contrast", "differentiate", "categorize"],
            "evaluate":   ["evaluate", "judge", "critique", "assess", "justify"],
            "create":     ["design", "create", "develop", "formulate", "propose"]
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_correct_answer_text(self, question: Dict[str, Any]) -> str:
        """
        Return the text of the correct answer option.

        Handles both:
          - options as a dict  {"A": "some text", "B": ...}  + correct_answer = "A"
          - options as a list  ["some text", ...]             + correct_answer = 0 / "0"
        """
        options = question.get("options", {})
        correct_key = question.get("correct_answer", "")

        if not correct_key or not options:
            return ""

        if isinstance(options, dict):
            # Normalise key — strip whitespace and match case-insensitively
            for key, value in options.items():
                if str(key).strip().upper() == str(correct_key).strip().upper():
                    return str(value)

        elif isinstance(options, list):
            try:
                idx = int(correct_key)
                return str(options[idx])
            except (ValueError, IndexError):
                pass

        return str(correct_key)  # fallback: return the raw answer string

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()

        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
            'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
            'because', 'until', 'while', 'although', 'though', 'this', 'that',
            'these', 'those', 'it', 'its', 'question', 'option', 'answer', 'correct'
        }

        return [w for w in words if w not in stopwords and len(w) > 2]

    def _calculate_topic_scores(self, text: str) -> Dict[str, float]:
        """Score each topic against the given text."""
        text_lower = text.lower()
        topic_scores = {}

        for topic, keywords in self.topic_keywords.items():
            score = 0.0
            for keyword in keywords:
                count = text_lower.count(keyword)
                if count > 0:
                    score += count * (1 + len(keyword) / 20)
            topic_scores[topic] = score

        return topic_scores

    def _detect_difficulty(self, question_text: str) -> str:
        """Detect difficulty from question text only."""
        text_lower = question_text.lower()
        scores = {"easy": 0, "medium": 0, "hard": 0}

        for difficulty, indicators in self.difficulty_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    scores[difficulty] += 1

        max_score = max(scores.values())
        if max_score == 0:
            return "medium"

        return max(scores, key=scores.get)

    def _detect_bloom_category(self, question_text: str) -> str:
        """Detect Bloom's taxonomy category from question text only."""
        text_lower = question_text.lower()
        bloom_scores = {cat: 0 for cat in self.bloom_categories}

        for category, verbs in self.bloom_categories.items():
            for verb in verbs:
                if verb in text_lower:
                    bloom_scores[category] += 1

        max_score = max(bloom_scores.values())
        if max_score == 0:
            return "understand"

        return max(bloom_scores, key=bloom_scores.get)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def tag_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tag a single question.

        Only the question text and the correct answer text are analysed.
        Returns the tagged question plus a 'confident' boolean flag.
        """
        question_text = question.get("question", "")
        correct_answer_text = self._get_correct_answer_text(question)

        # Combine ONLY question + correct answer for analysis
        analysis_text = question_text + " " + correct_answer_text

        # Topic scoring
        topic_scores = self._calculate_topic_scores(analysis_text)
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)

        # Top topics above threshold
        top_topics = [t for t, s in sorted_topics[:3] if s > 0]
        top_score = sorted_topics[0][1] if sorted_topics else 0
        confident = top_score >= self.CONFIDENCE_THRESHOLD

        # If nothing found, try raw keywords (still low-confidence)
        if not top_topics:
            keywords = self._extract_keywords(analysis_text)
            top_topics = keywords[:3] if keywords else ["general"]
            confident = False

        # Difficulty and Bloom's from question text only
        difficulty = self._detect_difficulty(question_text)
        bloom_category = self._detect_bloom_category(question_text)

        # Key concepts from combined text
        key_concepts = self._extract_keywords(analysis_text)[:5]

        tagged = question.copy()
        tagged["tags"]           = top_topics
        tagged["category"]       = top_topics[0] if top_topics else "general"
        tagged["difficulty"]     = difficulty
        tagged["bloom_category"] = bloom_category
        tagged["key_concepts"]   = key_concepts
        tagged["confident"]      = confident   # True = system is sure; False = ask user

        return tagged

    def tag_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch-tag questions (non-interactive)."""
        return [self.tag_question(q) for q in questions]

    def tag_questions_interactive(
        self,
        questions: List[Dict[str, Any]],
        available_tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Tag questions interactively.

        - If the system is confident  → auto-tag, show result, move on.
        - If the system is NOT confident  → show question + correct answer,
          display any available tags, and ask the user to type their tags.

        Args:
            questions:      List of question dicts.
            available_tags: Optional list of tag names to show as a menu
                            (loaded from the `tags` file, for example).
        """
        tagged_all = []
        total = len(questions)

        for idx, question in enumerate(questions, start=1):
            tagged = self.tag_question(question)

            q_text   = question.get("question", "(no question text)")
            ans_text = self._get_correct_answer_text(question) or question.get("correct_answer", "?")

            print(f"\n{'='*60}")
            print(f"Question {idx}/{total}")
            print(f"{'='*60}")
            print(f"Q: {q_text}")
            print(f"Correct Answer: {ans_text}")

            if tagged["confident"]:
                print(f"\n✅ Auto-tagged (system is confident):")
                print(f"   Tags        : {', '.join(tagged['tags'])}")
                print(f"   Difficulty  : {tagged['difficulty']}")
                print(f"   Bloom level : {tagged['bloom_category']}")
            else:
                print(f"\n⚠️  System is unsure about this question.")

                if available_tags:
                    print("\nAvailable tags:")
                    for i, tag in enumerate(available_tags, start=1):
                        print(f"  {i:2}. {tag}")

                print("\nPlease enter tags (comma-separated), or press Enter to keep auto-suggestions:")
                print(f"  Auto-suggestions → {', '.join(tagged['tags'])}")

                user_input = input("Your tags: ").strip()
                if user_input:
                    user_tags = [t.strip() for t in user_input.split(",") if t.strip()]
                    tagged["tags"]     = user_tags
                    tagged["category"] = user_tags[0] if user_tags else "general"
                    tagged["confident"] = True   # user confirmed

                print(f"\nEnter difficulty (easy / medium / hard) or press Enter to keep [{tagged['difficulty']}]:")
                diff_input = input("Difficulty: ").strip().lower()
                if diff_input in ("easy", "medium", "hard"):
                    tagged["difficulty"] = diff_input

                print(f"\nEnter Bloom's level (remember/understand/apply/analyze/evaluate/create)")
                print(f"or press Enter to keep [{tagged['bloom_category']}]:")
                bloom_input = input("Bloom level: ").strip().lower()
                if bloom_input in self.bloom_categories:
                    tagged["bloom_category"] = bloom_input

            tagged_all.append(tagged)

        print(f"\n{'='*60}")
        print(f"Tagging complete. {total} question(s) processed.")
        return tagged_all

    def get_tag_statistics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate tag/difficulty/Bloom's statistics across questions."""
        all_tags, difficulties, bloom_cats, categories = [], [], [], []

        for q in questions:
            all_tags.extend(q.get("tags", []))
            difficulties.append(q.get("difficulty", "unknown"))
            bloom_cats.append(q.get("bloom_category", "unknown"))
            categories.append(q.get("category", "unknown"))

        tag_counts        = Counter(all_tags)
        difficulty_counts = Counter(difficulties)
        bloom_counts      = Counter(bloom_cats)
        category_counts   = Counter(categories)

        return {
            "total_questions":       len(questions),
            "tag_distribution":      dict(tag_counts),
            "difficulty_distribution": dict(difficulty_counts),
            "bloom_distribution":    dict(bloom_counts),
            "category_distribution": dict(category_counts),
            "unique_tags":           list(tag_counts.keys()),
            "most_common_tags":      tag_counts.most_common(5),
            "most_common_difficulty": difficulty_counts.most_common(1)
        }

    def filter_questions_by_tag(
        self, questions: List[Dict[str, Any]], tag: str
    ) -> List[Dict[str, Any]]:
        return [q for q in questions if tag in q.get("tags", [])]

    def filter_questions_by_difficulty(
        self, questions: List[Dict[str, Any]], difficulty: str
    ) -> List[Dict[str, Any]]:
        return [q for q in questions if q.get("difficulty", "").lower() == difficulty.lower()]


# ------------------------------------------------------------------ #
#  Quick smoke-test                                                    #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    tagger = QuestionTagger()

    sample_questions = [
        {
            "question": "What is the purpose of the attention mechanism in transformers?",
            "options": {
                "A": "To reduce model size",
                "B": "To allow the model to focus on relevant parts of the input",
                "C": "To speed up training",
                "D": "To add non-linearity"
            },
            "correct_answer": "B",
        },
        {
            "question": "Which ancient capital city is now partially covered by a modern metropolis?",
            "options": {
                "A": "London",
                "B": "Tenochtitlan (now Mexico City)",
                "C": "Paris",
                "D": "Istanbul"
            },
            "correct_answer": "B",
        },
    ]

    print("=== Non-interactive batch tagging ===\n")
    tagged = tagger.tag_questions(sample_questions)
    for i, q in enumerate(tagged, 1):
        print(f"Q{i}: {q['question']}")
        print(f"  Correct answer text : {tagger._get_correct_answer_text(sample_questions[i-1])}")
        print(f"  Tags      : {q['tags']}")
        print(f"  Difficulty: {q['difficulty']}")
        print(f"  Bloom     : {q['bloom_category']}")
        print(f"  Confident : {q['confident']}")
        print()
