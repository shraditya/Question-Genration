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
                    max_completion_tokens=1500,
                    top_p=1,
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

    # Comprehensive main category taxonomy
    ALLOWED_TAGS = [
        "Science",
        "Mathematics",
        "Statistics & Data Science",
        "Computer Science",
        "Engineering",
        "Technology",
        "Medical & Health Sciences",
        "Social Sciences",
        "Economics",
        "Political Science",
        "Law",
        "Business & Management",
        "History",
        "Geography",
        "Literature",
        "Arts & Culture",
        "Sports & Games",
        "Education",
        "General Knowledge"
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


    def auto_tag_hierarchical(self, question_text: str, correct_answer_text: str = "") -> dict:
        """
        Ask Groq to classify the question with context-based hierarchical tags.

        Returns: {"main_tag": "Computer Science", "sub_tags": ["DNN", "ML", "NLP"]}

        Sub-tags are generated based on the specific question context, not a fixed taxonomy.
        Example: "What is deep learning?" → Main: "Computer Science", Subs: ["DNN", "ML", "Deep Learning"]
        """
        answer_part = f" (Answer: {correct_answer_text[:50]})" if correct_answer_text else ""

        # Clearer prompt with valid JSON example
        prompt = (
            f"Classify this question:\n"
            f"1. Pick 1 main category from: {', '.join(self.ALLOWED_TAGS[:10])}, etc\n"
            f"2. Generate 3-4 specific sub-topics based on the question's context\n\n"
            f"Question: {question_text[:120]}{answer_part}\n\n"
            f"Reply ONLY with valid JSON:\n"
            f'{{\"main_tag\": \"Category Name\", \"sub_tags\": [\"Sub1\", \"Sub2\", \"Sub3\"]}}'
        )

        try:
            response = self._make_api_call_with_retry(prompt)
            # Extract JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                data = json.loads(response[start:end])

                # Validate main_tag
                main_tag = data.get("main_tag", "General Knowledge")
                if main_tag not in self.ALLOWED_TAGS:
                    # Try to match
                    for allowed in self.ALLOWED_TAGS:
                        if allowed.lower() in main_tag.lower() or main_tag.lower() in allowed.lower():
                            main_tag = allowed
                            break
                    else:
                        main_tag = "General Knowledge"

                # Get context-based sub_tags (max 4)
                sub_tags = data.get("sub_tags", [])
                if not isinstance(sub_tags, list):
                    sub_tags = [str(sub_tags)]

                # Clean and limit to 3-4 sub-tags
                sub_tags = [str(s).strip() for s in sub_tags if str(s).strip()][:4]

                if not sub_tags:
                    sub_tags = ["General"]

                return {"main_tag": main_tag, "sub_tags": sub_tags}
        except Exception as e:
            print(f"      Error in hierarchical tagging: {e}")

        return {"main_tag": "General Knowledge", "sub_tags": ["General"]}

    def _tag_batch_hierarchical(self, batch: list) -> list:
        """
        Tag a batch of questions in ONE API call for speed.
        Returns list of {"main_tag": str, "sub_tags": [str]} dicts.
        """
        if not batch:
            return []

        # Build compact question list
        lines = []
        for idx, q in enumerate(batch, 1):
            q_text = q.get('question', '')[:80]
            ans_key = q.get('correct_answer', '')
            lines.append(f"{idx}.{q_text} (Ans:{ans_key})")

        questions_text = "\n".join(lines)

        prompt = (
            f"Tag {len(batch)} questions. For each:\n"
            f"1. Main category from: {', '.join(self.ALLOWED_TAGS[:12])}, etc\n"
            f"2. 3-4 context-based sub-tags\n\n"
            f"{questions_text}\n\n"
            f"Reply ONLY valid JSON array:\n"
            f'[{{\"main_tag\":\"X\",\"sub_tags\":[\"A\",\"B\",\"C\"]}}]'
        )

        try:
            response = self._make_api_call_with_retry(prompt)
            # Extract JSON array
            start = response.find('[')
            end = response.rfind(']') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array in response")

            data = json.loads(response[start:end])
            if not isinstance(data, list):
                raise ValueError("Response not a list")

            # Validate and clean
            results = []
            for item in data:
                main_tag = item.get("main_tag", "General Knowledge")
                # Validate main_tag
                if main_tag not in self.ALLOWED_TAGS:
                    for allowed in self.ALLOWED_TAGS:
                        if allowed.lower() in main_tag.lower():
                            main_tag = allowed
                            break
                    else:
                        main_tag = "General Knowledge"

                sub_tags = item.get("sub_tags", [])
                if not isinstance(sub_tags, list):
                    sub_tags = [str(sub_tags)]
                sub_tags = [str(s).strip() for s in sub_tags if str(s).strip()][:4]

                if not sub_tags:
                    sub_tags = ["General"]

                results.append({"main_tag": main_tag, "sub_tags": sub_tags})

            # Pad if needed
            while len(results) < len(batch):
                results.append({"main_tag": "General Knowledge", "sub_tags": ["General"]})

            return results[:len(batch)]

        except Exception as e:
            print(f"   ⚠️  Batch error: {str(e)[:50]}")
            return [{"main_tag": "General Knowledge", "sub_tags": ["General"]}
                    for _ in range(len(batch))]

    def llm_tag_questions(self, questions: list, batch_size: int = 10, max_workers: int = 3) -> list:
        """
        Fast batch tagging with parallel workers.

        Args:
            questions: List of question dicts
            batch_size: Questions per API call (default 10 for speed/stability balance)
            max_workers: Parallel workers (default 3 to avoid rate limits)

        Performance: 104 questions ≈ 30-60 seconds (vs 5+ minutes one-by-one)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        total = len(questions)
        batches = [questions[i:i + batch_size]
                   for i in range(0, total, batch_size)]

        print(f"\n🤖 Fast batch tagging {total} question(s) | "
              f"batch={batch_size} | workers={max_workers} | batches={len(batches)}")

        # Thread-safe progress
        done_count = [0]
        lock = threading.Lock()
        results = [None] * len(batches)

        def process_batch(args):
            batch_idx, batch = args
            tag_dicts = self._tag_batch_hierarchical(batch)
            with lock:
                done_count[0] += 1
                pct = 100 * done_count[0] / len(batches)
                qs_done = min(done_count[0] * batch_size, total)
                print(f"   [{qs_done}/{total}]  {pct:.0f}% complete")
            return batch_idx, tag_dicts

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(process_batch, (i, b)): i
                for i, b in enumerate(batches)
            }
            for future in as_completed(futures):
                batch_idx, tag_dicts = future.result()
                results[batch_idx] = tag_dicts

        # Apply tags back to questions
        for batch_idx, batch in enumerate(batches):
            tags_for_batch = results[batch_idx] or [
                {"main_tag": "General Knowledge", "sub_tags": ["General"]}
                for _ in range(len(batch))
            ]
            for q, tag_dict in zip(batch, tags_for_batch):
                main_tag = tag_dict["main_tag"]
                sub_tags = tag_dict["sub_tags"]

                # Only add main_tag and sub_tags (remove redundant fields)
                q['main_tag'] = main_tag
                q['sub_tags'] = sub_tags

        tagged = sum(1 for q in questions if q.get('main_tag'))
        print(f"\n✅ Done — {tagged}/{total} questions tagged.")
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