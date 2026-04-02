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

        # Trim to requested number before heavy LLM deduplication
        all_mcqs = all_mcqs[:num_questions * 2]  # keep a buffer for filtering
        unique_mcqs = self._remove_duplicate_questions(all_mcqs)
        
        # NEW: LLM intent-based deduplication and similarity filter
        intent_unique_mcqs = self.llm_filter_by_intent(unique_mcqs)
        
        # Finally, trim to exactly the target number requested
        intent_unique_mcqs = intent_unique_mcqs[:num_questions]
        
        tagged_mcqs = self.tag_questions(intent_unique_mcqs)
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

    def llm_filter_by_intent(self, mcqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use the LLM to extract the core intent of each question, compute similarity, 
        and filter out questions that test the exact same concept.
        Also adds the 'intent' field to each kept question so the user can see it.
        """
        if len(mcqs) <= 1:
            return mcqs

        print("\n🧠 Using LLM for intent-based similarity filtering...")
        
        lines = []
        for idx, q in enumerate(mcqs, 1):
            q_text = q.get('question', '')
            ans_text = self._resolve_answer_text(q)
            lines.append(f"[{idx}] Q: {q_text}\n    A: {ans_text}")
            
        questions_block = "\n".join(lines)
        
        prompt = (
            "You are an expert exam reviewer.\n"
            "Analyze the following multiple choice questions.\n"
            "For each question, determine its exact 'core intent' (the specific concept or fact being tested).\n"
            "Then, identify if any questions are semantically identical to each other in intent (i.e. they test the identical underlying concept and have equivalent answers). "
            "If there are duplicates, pick the single best version to 'keep', and mark the rest to be filtered out.\n\n"
            "Return a JSON array where each object corresponds to a KEEP question, with the following format:\n"
            "[\n"
            "  {\n"
            "    \"index\": 1,\n"
            "    \"intent\": \"Tests knowledge of the Sigmoid function for probability mapping\",\n"
            "    \"similarity_dropped\": [list of indices of any questions that were filtered out because they had the same intent (empty if none)]\n"
            "  }\n"
            "]\n\n"
            "Questions to evaluate:\n"
            f"{questions_block}\n\n"
            "Output ONLY the JSON array (no other text):"
        )

        try:
            response = self._make_api_call_with_retry(prompt)
            data = self._extract_json_from_response(response)
            
            if isinstance(data, list):
                keep_indices = set()
                intent_map = {}
                for item in data:
                    idx = item.get("index")
                    if isinstance(idx, int) and 1 <= idx <= len(mcqs):
                        keep_indices.add(idx)
                        intent_map[idx] = item.get("intent", "General Concept")
                
                filtered_mcqs = []
                for i, q in enumerate(mcqs, 1):
                    if i in keep_indices:
                        q['intent'] = intent_map.get(i, "")
                        filtered_mcqs.append(q)
                
                print(f"✅ LLM Intent Filter: Retained {len(filtered_mcqs)} unique questions out of {len(mcqs)}")
                return filtered_mcqs
                
        except Exception as e:
            print(f"❌ Error during LLM intent filtering: {e}")
            
        return mcqs

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


    def _resolve_answer_text(self, q: dict) -> str:
        """Extract the correct answer text from a question dict."""
        options = q.get('options', {})
        ans_key = q.get('correct_answer', '')
        if isinstance(options, dict):
            return next(
                (v for k, v in options.items()
                 if str(k).strip().upper() == str(ans_key).strip().upper()),
                str(ans_key)
            )
        return str(ans_key)

    def _tag_batch(self, batch: list) -> list:
        """
        Send a batch of questions to Groq in ONE API call.
        Returns a list of tag strings (same length as batch).
        Each tag is guaranteed to be one of ALLOWED_TAGS.
        """
        tag_list = "\n".join(f"- {t}" for t in self.ALLOWED_TAGS)

        # Build the numbered question list
        lines = []
        for idx, q in enumerate(batch, 1):
            q_text   = q.get('question', '')
            ans_text = self._resolve_answer_text(q)
            lines.append(f"{idx}. Q: {q_text}\n   Answer: {ans_text}")
        questions_block = "\n\n".join(lines)

        prompt = (
            "You are an exam question classifier.\n"
            "Classify each question below into EXACTLY ONE category from this list:\n\n"
            f"{tag_list}\n\n"
            "Rules:\n"
            "- Return ONLY a valid JSON array with one tag per question, in order.\n"
            "- Each tag must be copied exactly from the list above.\n"
            "- Use \"General Knowledge\" if unsure.\n"
            "- No explanations, no extra text — ONLY the JSON array.\n\n"
            "Example output for 3 questions:\n"
            "[\"Science\", \"Geography\", \"History\"]\n\n"
            f"Questions:\n{questions_block}\n\n"
            "JSON array of tags:"
        )

        try:
            response = self._make_api_call_with_retry(prompt)

            # Extract JSON array from response
            start = response.find('[')
            end   = response.rfind(']') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array found in response")

            raw_tags = json.loads(response[start:end])

            # Validate & map each returned tag to ALLOWED_TAGS
            validated = []
            allowed_lower = {t.lower(): t for t in self.ALLOWED_TAGS}
            for raw in raw_tags:
                raw_s = str(raw).strip().strip('"\'')
                # Exact match (case-insensitive)
                tag = allowed_lower.get(raw_s.lower())
                if not tag:
                    # Partial match
                    tag = next(
                        (t for t in self.ALLOWED_TAGS
                         if t.lower() in raw_s.lower() or raw_s.lower() in t.lower()),
                        "General Knowledge"
                    )
                validated.append(tag)

            # Pad/trim to match batch size
            while len(validated) < len(batch):
                validated.append("General Knowledge")
            return validated[:len(batch)]

        except Exception as e:
            # On any failure, fall back to General Knowledge for the whole batch
            return ["General Knowledge"] * len(batch)

    def llm_tag_questions(self, questions: list,
                          batch_size: int = 50,
                          max_workers: int = 5) -> list:
        """
        Tag a list of questions using Groq LLM with batching + parallel workers.

        Performance vs sequential:
          1 q/call  → 5 000 qs ≈ 83 min
          batch=50  → 5 000 qs ≈  4 min
          batch=50 + 5 workers → 5 000 qs ≈ < 1 min

        Args:
            questions:   List of question dicts.
            batch_size:  Questions per API call  (default 50).
            max_workers: Parallel API calls       (default 5).
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        total   = len(questions)
        batches = [questions[i:i + batch_size]
                   for i in range(0, total, batch_size)]

        print(f"\n🤖 LLM tagging {total} question(s) | "
              f"batch={batch_size} | workers={max_workers} | "
              f"batches={len(batches)}")

        # Thread-safe progress counter
        done_count = [0]
        lock = threading.Lock()

        # results[batch_index] = list of tags for that batch
        results = [None] * len(batches)

        def process_batch(args):
            batch_idx, batch = args
            tags = self._tag_batch(batch)
            with lock:
                done_count[0] += 1
                pct = 100 * done_count[0] / len(batches)
                qs_done = min((done_count[0]) * batch_size, total)
                print(f"   [{qs_done}/{total}]  {pct:.0f}% complete", flush=True)
            return batch_idx, tags

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(process_batch, (i, b)): i
                for i, b in enumerate(batches)
            }
            for future in as_completed(futures):
                batch_idx, tags = future.result()
                results[batch_idx] = tags

        # Apply tags back to questions in original order
        for batch_idx, batch in enumerate(batches):
            tags_for_batch = results[batch_idx] or ["General Knowledge"] * len(batch)
            for q, tag in zip(batch, tags_for_batch):
                q['tags'] = [tag]

        tagged = sum(1 for q in questions if q.get('tags'))
        print(f"\n✅ Done — {tagged}/{total} question(s) tagged.")
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
