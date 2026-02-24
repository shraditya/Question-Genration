import re
from typing import List, Dict, Any, Tuple
from collections import Counter
import numpy as np


class QuestionTagger:
    """ML-based question tagging system using keyword matching and text analysis"""

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
            "remember": ["define", "list", "recall", "name", "state", "identify"],
            "understand": ["explain", "describe", "summarize", "paraphrase", "interpret"],
            "apply": ["apply", "use", "demonstrate", "solve", "implement"],
            "analyze": ["analyze", "compare", "contrast", "differentiate", "categorize"],
            "evaluate": ["evaluate", "judge", "critique", "assess", "justify"],
            "create": ["design", "create", "develop", "formulate", "propose"]
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)

        # Split into words
        words = text.split()

        # Remove stopwords and short words
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

        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords

    def _calculate_topic_scores(self, text: str) -> Dict[str, float]:
        """Calculate relevance scores for each topic"""
        text_lower = text.lower()
        topic_scores = {}

        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                count = text_lower.count(keyword)
                if count > 0:
                    # Weight by frequency and keyword specificity
                    score += count * (1 + len(keyword) / 20)

            topic_scores[topic] = score

        return topic_scores

    def _detect_difficulty(self, question_text: str) -> str:
        """Detect question difficulty level"""
        text_lower = question_text.lower()
        difficulty_scores = {"easy": 0, "medium": 0, "hard": 0}

        for difficulty, indicators in self.difficulty_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    difficulty_scores[difficulty] += 1

        # Return the difficulty with highest score
        max_score = max(difficulty_scores.values())
        if max_score == 0:
            return "medium"  # Default to medium if no indicators found

        for difficulty, score in difficulty_scores.items():
            if score == max_score:
                return difficulty

        return "medium"

    def _detect_bloom_category(self, question_text: str) -> str:
        """Detect Bloom's taxonomy category"""
        text_lower = question_text.lower()
        bloom_scores = {category: 0 for category in self.bloom_categories}

        for category, verbs in self.bloom_categories.items():
            for verb in verbs:
                if verb in text_lower:
                    bloom_scores[category] += 1

        max_score = max(bloom_scores.values())
        if max_score == 0:
            return "understand"  # Default category

        for category, score in bloom_scores.items():
            if score == max_score:
                return category

        return "understand"

    def tag_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add tags to a single question

        Args:
            question: Dictionary with question data

        Returns:
            Question dictionary with added tags
        """
        # Combine question text and options for analysis
        text_to_analyze = question.get("question", "")

        # Add options to analysis text
        options = question.get("options", {})
        for opt_key, opt_value in options.items():
            text_to_analyze += " " + str(opt_value)

        # Add explanation to analysis text
        explanation = question.get("explanation", "")
        text_to_analyze += " " + explanation

        # Calculate topic scores
        topic_scores = self._calculate_topic_scores(text_to_analyze)

        # Get top topics (score > 0)
        tagged_topics = [topic for topic, score in topic_scores.items() if score > 0]

        # Sort by score and take top 3
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        top_topics = [topic for topic, score in sorted_topics[:3] if score > 0]

        # If no topics found, use extracted keywords
        if not top_topics:
            keywords = self._extract_keywords(text_to_analyze)
            top_topics = keywords[:3] if keywords else ["general"]

        # Detect difficulty
        difficulty = self._detect_difficulty(question.get("question", ""))

        # Detect Bloom's category
        bloom_category = self._detect_bloom_category(question.get("question", ""))

        # Extract key concepts from the question
        keywords = self._extract_keywords(text_to_analyze)
        key_concepts = keywords[:5] if keywords else []

        # Build the tagged question
        tagged_question = question.copy()
        tagged_question["tags"] = top_topics
        tagged_question["category"] = top_topics[0] if top_topics else "general"
        tagged_question["difficulty"] = difficulty
        tagged_question["bloom_category"] = bloom_category
        tagged_question["key_concepts"] = key_concepts

        return tagged_question

    def tag_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add tags to multiple questions

        Args:
            questions: List of question dictionaries

        Returns:
            List of question dictionaries with added tags
        """
        tagged_questions = []
        for question in questions:
            tagged_question = self.tag_question(question)
            tagged_questions.append(tagged_question)

        return tagged_questions

    def get_tag_statistics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about tags across all questions

        Args:
            questions: List of tagged question dictionaries

        Returns:
            Dictionary with tag statistics
        """
        all_tags = []
        difficulties = []
        bloom_categories = []
        categories = []

        for question in questions:
            all_tags.extend(question.get("tags", []))
            difficulties.append(question.get("difficulty", "unknown"))
            bloom_categories.append(question.get("bloom_category", "unknown"))
            categories.append(question.get("category", "unknown"))

        tag_counts = Counter(all_tags)
        difficulty_counts = Counter(difficulties)
        bloom_counts = Counter(bloom_categories)
        category_counts = Counter(categories)

        return {
            "total_questions": len(questions),
            "tag_distribution": dict(tag_counts),
            "difficulty_distribution": dict(difficulty_counts),
            "bloom_distribution": dict(bloom_counts),
            "category_distribution": dict(category_counts),
            "unique_tags": list(tag_counts.keys()),
            "most_common_tags": tag_counts.most_common(5),
            "most_common_difficulty": difficulty_counts.most_common(1)
        }

    def filter_questions_by_tag(
        self,
        questions: List[Dict[str, Any]],
        tag: str
    ) -> List[Dict[str, Any]]:
        """
        Filter questions by a specific tag

        Args:
            questions: List of tagged question dictionaries
            tag: Tag to filter by

        Returns:
            Filtered list of questions
        """
        filtered = []
        for question in questions:
            if tag in question.get("tags", []):
                filtered.append(question)
        return filtered

    def filter_questions_by_difficulty(
        self,
        questions: List[Dict[str, Any]],
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """
        Filter questions by difficulty level

        Args:
            questions: List of tagged question dictionaries
            difficulty: Difficulty level (easy/medium/hard)

        Returns:
            Filtered list of questions
        """
        filtered = []
        for question in questions:
            if question.get("difficulty", "").lower() == difficulty.lower():
                filtered.append(question)
        return filtered


# Demo/test function
if __name__ == "__main__":
    # Test the tagger
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
            "explanation": "The attention mechanism allows the model to weigh different parts of the input differently."
        },
        {
            "question": "Calculate the F1 score given precision=0.8 and recall=0.6",
            "options": {
                "A": "0.69",
                "B": "0.72",
                "C": "0.65",
                "D": "0.75"
            },
            "correct_answer": "A",
            "explanation": "F1 = 2 * (precision * recall) / (precision + recall) = 2 * (0.8 * 0.6) / (0.8 + 0.6) = 0.69"
        }
    ]

    tagged = tagger.tag_questions(sample_questions)

    print("=== Tagged Questions ===\n")
    for i, q in enumerate(tagged, 1):
        print(f"Question {i}:")
        print(f"  Text: {q['question']}")
        print(f"  Tags: {q['tags']}")
        print(f"  Category: {q['category']}")
        print(f"  Difficulty: {q['difficulty']}")
        print(f"  Bloom's Category: {q['bloom_category']}")
        print(f"  Key Concepts: {q['key_concepts']}")
        print()

    print("=== Tag Statistics ===\n")
    stats = tagger.get_tag_statistics(tagged)
    print(f"Total Questions: {stats['total_questions']}")
    print(f"Tag Distribution: {stats['tag_distribution']}")
    print(f"Difficulty Distribution: {stats['difficulty_distribution']}")
    print(f"Bloom Distribution: {stats['bloom_distribution']}")
