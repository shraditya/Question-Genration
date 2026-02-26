import json
import re
import time
from typing import List, Dict, Any
from groq import Groq
from config import Config
from question_tagger import QuestionTagger


class MCQGenerator:
    """Generate MCQs using Groq LLM (openai/gpt-oss-120b)"""

    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.tagger = QuestionTagger()
        print(f"✅ Connected to Groq API | Model: {self.model}")

    def generate_mcq_prompt(self, context: str, num_questions: int = 5) -> str:
        """Generate prompt for MCQ creation"""
        prompt = f"""Based on the following text context, generate {num_questions} multiple choice questions (MCQs).

Requirements:
1. Questions should be clear, understandable, and test comprehension
2. Each question should have exactly 4 options (A, B, C, D)
3. Only one option should be correct
4. Questions should cover different aspects of the content
5. No repeated questions
6. Questions should be at an appropriate difficulty level

Text Context:
{context}

Generate the MCQs in the following JSON format (only return valid JSON, no extra text):
{{
    "questions": [
        {{
            "question": "Question text here?",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Brief explanation of why this is correct"
        }}
    ]
}}"""
        return prompt

    def _make_api_call_with_retry(self, prompt: str) -> str:
        """Make streaming API call to Groq with retry logic"""
        for attempt in range(Config.LLM_RETRIES):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=1,
                    max_completion_tokens=8192,
                    top_p=1,
                    reasoning_effort="medium",
                    stream=True,
                    stop=None
                )

                # Collect streamed chunks into full response
                full_response = ""
                for chunk in completion:
                    delta = chunk.choices[0].delta.content or ""
                    full_response += delta

                return full_response

            except Exception as e:
                if attempt < Config.LLM_RETRIES - 1:
                    print(f"API call failed (attempt {attempt + 1}/{Config.LLM_RETRIES}): {str(e)}")
                    time.sleep(Config.LLM_RETRY_DELAY)
                else:
                    raise e

        return ""

    def generate_mcqs(self, context_chunks: List[str], num_questions: int = 10) -> List[Dict[str, Any]]:
        """Generate MCQs from context chunks"""
        if not context_chunks:
            raise ValueError("No context chunks provided")

        all_mcqs = []
        questions_per_chunk = max(1, num_questions // len(context_chunks))

        for chunk in context_chunks:
            try:
                prompt = self.generate_mcq_prompt(chunk, questions_per_chunk)
                response_text = self._make_api_call_with_retry(prompt)
                mcq_data = self._extract_json_from_response(response_text)

                if mcq_data and "questions" in mcq_data:
                    # Validate each MCQ before adding
                    for mcq in mcq_data["questions"]:
                        if self.validate_mcq_format(mcq):
                            all_mcqs.append(mcq)

            except Exception as e:
                print(f"Error generating MCQs for chunk: {str(e)}")
                continue

        # Trim, deduplicate, tag
        all_mcqs = all_mcqs[:num_questions]
        unique_mcqs = self._remove_duplicate_questions(all_mcqs)
        tagged_mcqs = self.tag_questions(unique_mcqs)
        return tagged_mcqs

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON data from LLM response"""
        try:
            # Try direct parse first
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            pass

        try:
            # Try to find outermost JSON object
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")

        return None

    def _remove_duplicate_questions(self, mcqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate questions based on question text"""
        seen_questions = set()
        unique_mcqs = []

        for mcq in mcqs:
            question_text = mcq.get("question", "").lower().strip()
            if question_text and question_text not in seen_questions:
                seen_questions.add(question_text)
                unique_mcqs.append(mcq)

        return unique_mcqs

    def refine_mcqs(self, original_mcqs: List[Dict[str, Any]], feedback: str) -> List[Dict[str, Any]]:
        """Refine MCQs based on user feedback"""
        if not original_mcqs:
            return []

        # Build context with full original MCQs
        context = "Original questions with options:\n"
        for i, mcq in enumerate(original_mcqs, 1):
            context += f"\n{i}. {mcq.get('question', '')}\n"
            for opt, text in mcq.get('options', {}).items():
                context += f"   {opt}. {text}\n"
            context += f"   Answer: {mcq.get('correct_answer', '')}\n"

        context += f"\nUser feedback: {feedback}\n"
        context += "\nPlease generate improved questions addressing the feedback."

        try:
            prompt = self.generate_mcq_prompt(context, len(original_mcqs))
            response_text = self._make_api_call_with_retry(prompt)
            refined_data = self._extract_json_from_response(response_text)

            if refined_data and "questions" in refined_data:
                return self.tag_questions(refined_data["questions"])

        except Exception as e:
            print(f"Error refining MCQs: {str(e)}")

        return original_mcqs

    def validate_mcq_format(self, mcq: Dict[str, Any]) -> bool:
        """Validate MCQ format"""
        required_fields = ["question", "options", "correct_answer", "explanation"]

        for field in required_fields:
            if field not in mcq:
                return False

        if not isinstance(mcq["options"], dict) or len(mcq["options"]) != 4:
            return False

        if mcq["correct_answer"] not in ["A", "B", "C", "D"]:
            return False

        return True

    def tag_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add ML-based tags to questions"""
        return self.tagger.tag_questions(questions)

    def get_tag_statistics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about question tags"""
        return self.tagger.get_tag_statistics(questions)

    def filter_questions_by_tag(
        self,
        questions: List[Dict[str, Any]],
        tag: str
    ) -> List[Dict[str, Any]]:
        """Filter questions by a specific tag"""
        return self.tagger.filter_questions_by_tag(questions, tag)

    # Fixed tag taxonomy — LLM must pick exactly one
    ALLOWED_TAGS = [
        "Science",           # Biology, Chemistry, Physics, Astronomy, Earth Science
        "Geography",         # Countries, Capitals, Landmarks, Physical Features
        "History",           # Events, Leaders, Wars, Timelines
        "Technology",        # Computing, AI, Programming, Digital Terms
        "Mathematics",       # Arithmetic, Algebra, Geometry, Logic
        "Literature",        # Authors, Books, Poetry, Drama
        "Arts & Culture",    # Music, Painting, Film, Traditions
        "Sports & Games",    # Rules, Events, Athletes, Records
        "General Knowledge", # Mixed/ambiguous questions (fallback)
    ]

    def auto_tag_category(self, question_text: str, correct_answer_text: str = "") -> str:
        """
        Ask Groq to classify the question into exactly ONE tag from ALLOWED_TAGS.
        Uses question text + correct answer text only.
        Returns the matched tag string (always non-empty — falls back to 'General Knowledge').
        """
        tag_list = "\n".join(f"- {t}" for t in self.ALLOWED_TAGS)
        answer_part = f"\nCorrect Answer: {correct_answer_text}" if correct_answer_text else ""

        prompt = (
            "You are an exam question classifier.\n"
            "Read the question and its correct answer, then pick EXACTLY ONE category "
            "from the list below that best describes what this question is testing.\n\n"
            "Allowed categories (pick only from this list, exact spelling):\n"
            f"{tag_list}\n\n"
            "Rules:\n"
            "- Reply with ONLY the category name, nothing else.\n"
            "- Use the exact spelling from the list above.\n"
            "- If the question does not fit any specific category, reply: General Knowledge\n\n"
            f"Question: {question_text}"
            f"{answer_part}\n\nCategory:"
        )
        try:
            response = self._make_api_call_with_retry(prompt)
            line = response.strip().split('\n')[0].strip().strip('"\'.,;')

            # Match against allowed tags (case-insensitive)
            for tag in self.ALLOWED_TAGS:
                if tag.lower() == line.lower():
                    return tag

            # Partial match fallback
            for tag in self.ALLOWED_TAGS:
                if tag.lower() in line.lower() or line.lower() in tag.lower():
                    return tag

            return "General Knowledge"  # ultimate fallback
        except Exception:
            return "General Knowledge"


    def llm_tag_questions(self, questions: list) -> list:
        """
        Tag every question using the Groq LLM (question text + correct answer only).
        Only the 'tags' field is added/updated on each question.
          - LLM confident  → tags = ["topic1", "topic2"]
          - LLM unsure     → tags = []  (user fills in via option 8)
        """
        print(f"\n🤖 LLM tagging {len(questions)} question(s) via Groq...")

        for i, q in enumerate(questions, 1):
            q_text  = q.get('question', '')
            options = q.get('options', {})
            ans_key = q.get('correct_answer', '')
            if isinstance(options, dict):
                ans_text = next(
                    (v for k, v in options.items()
                     if str(k).strip().upper() == str(ans_key).strip().upper()),
                    str(ans_key)
                )
            else:
                ans_text = str(ans_key)

            tag_str = self.auto_tag_category(q_text, ans_text)

            if tag_str:
                q['tags'] = [t.strip() for t in tag_str.split(',') if t.strip()]
                status    = f"✅ → {tag_str}"
            else:
                q['tags'] = []          # empty = needs manual input
                status    = "⚠️  unsure — needs manual input"

            print(f"   [{i}/{len(questions)}] {status}")

        return questions

    def auto_tag_questions(self, questions: list) -> list:
        """Backward-compat wrapper → delegates to llm_tag_questions."""
        return self.llm_tag_questions(questions)


    def filter_questions_by_difficulty(
        self,
        questions: List[Dict[str, Any]],
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Filter questions by difficulty level"""
        return self.tagger.filter_questions_by_difficulty(questions, difficulty)
