#!/usr/bin/env python3
"""
Terminal-based RAG MCQ Generator
Run this directly in the terminal without Streamlit
"""

import os
import sys
from typing import List, Dict, Any
import json
from itertools import combinations
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from document_processor import DocumentProcessor
from rag_system import RAGSystem
from mcq_generator import MCQGenerator
from config import Config


SIMILARITY_MODEL_PATH = os.getenv('MODEL_PATH', '/Users/k/rag_questions/similiarty /mcq_intent_model')
CUTOFF_THRESHOLD = 0.75
DUPLICATE_THRESHOLD = 0.90
HIGH_SIMILARITY_THRESHOLD = 0.80

class TerminalMCQApp:
    """Terminal-based MCQ Generation Application"""
    
    def __init__(self):
        self.rag_system = None
        self.mcq_generator = None
        self.similarity_model = None
        self.current_mcqs = []
        self.document_text = ""
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize RAG system and MCQ generator"""
        try:
            print("📚 Initializing RAG System...")
            self.rag_system = RAGSystem()
            
            print("🤖 Initializing MCQ Generator...")
            self.mcq_generator = MCQGenerator()
            
            print("✅ All components initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing components: {str(e)}")
            sys.exit(1)

    def _load_similarity_model(self):
        """Load only the fine-tuned similarity model (no fallback)."""
        if self.similarity_model is not None:
            return self.similarity_model

        model_dir = Path(SIMILARITY_MODEL_PATH)
        expected_weight_files = [
            model_dir / 'model.safetensors',
            model_dir / 'pytorch_model.bin',
        ]
        if not model_dir.exists():
            raise RuntimeError(
                f"Fine-tuned model path does not exist: '{SIMILARITY_MODEL_PATH}'. "
                "Set MODEL_PATH to your trained model directory."
            )
        if not any(p.exists() for p in expected_weight_files):
            raise RuntimeError(
                "Fine-tuned model is incomplete. Missing weight file in "
                f"'{SIMILARITY_MODEL_PATH}'. Expected one of: model.safetensors, pytorch_model.bin. "
                "Re-export your trained model with model.save_pretrained(<path>) and tokenizer.save_pretrained(<path>)."
            )

        print(f"🧠 Loading similarity model from: {SIMILARITY_MODEL_PATH}")
        try:
            self.similarity_model = SentenceTransformer(SIMILARITY_MODEL_PATH)
            print("✅ Similarity model loaded")
        except Exception as e:
            raise RuntimeError(
                f"Could not load fine-tuned similarity model from '{SIMILARITY_MODEL_PATH}': {e}"
            )

        return self.similarity_model

    def _resolve_answer_text(self, mcq: Dict[str, Any]) -> str:
        """Resolve answer text from the MCQ shape (letter or direct text)."""
        answer = str(mcq.get('correct_answer', '')).strip()
        options = mcq.get('options', {}) or {}

        if isinstance(options, dict) and answer in options:
            return str(options.get(answer, '')).strip()

        return answer

    def _sync_hierarchical_tag_fields(self, mcq: Dict[str, Any]) -> Dict[str, Any]:
        """Mirror hierarchical tags into legacy display/export fields."""
        main_tag = mcq.get('main_tag') or mcq.get('category') or ''
        sub_tags = mcq.get('sub_tags') or []

        if isinstance(sub_tags, str):
            sub_tags = [s.strip() for s in sub_tags.split(',') if s.strip()]
        elif not isinstance(sub_tags, list):
            sub_tags = [str(sub_tags).strip()] if str(sub_tags).strip() else []

        if main_tag:
            mcq['main_tag'] = main_tag
            mcq['category'] = main_tag

        if sub_tags:
            mcq['sub_tags'] = sub_tags[:3]

        legacy_tags = []
        if main_tag:
            legacy_tags.append(main_tag)
        for tag in sub_tags:
            if tag and tag not in legacy_tags:
                legacy_tags.append(tag)

        if legacy_tags:
            mcq['tags'] = legacy_tags

        return mcq

    def _calculate_adaptive_similarity(self, q_sim: float, a_sim: float):
        """Use the same adaptive weighting used in main.py."""
        answer_weight = 0.15 + 0.70 * (1.0 - q_sim)
        question_weight = 1.0 - answer_weight
        final_sim = answer_weight * a_sim + question_weight * q_sim
        return final_sim, answer_weight

    def _classify_similarity(self, sim_score: float) -> str:
        """Classify similarity level based on shared thresholds."""
        if sim_score >= DUPLICATE_THRESHOLD:
            return 'Duplicate'
        if sim_score >= HIGH_SIMILARITY_THRESHOLD:
            return 'Highly Similar'
        if sim_score >= CUTOFF_THRESHOLD:
            return 'Similar'
        return 'Different'

    def _find_similar_tagged_questions(self, threshold: float = CUTOFF_THRESHOLD) -> List[Dict[str, Any]]:
        """Find similar question pairs and include tag-level overlap details."""
        if len(self.current_mcqs) < 2:
            return []

        model = self._load_similarity_model()

        questions = [str(q.get('question', '')).strip() for q in self.current_mcqs]
        answers = [self._resolve_answer_text(q) for q in self.current_mcqs]

        q_embs = model.encode(questions, batch_size=128, normalize_embeddings=True)
        a_embs = model.encode(answers, batch_size=128, normalize_embeddings=True)

        q_mat = cosine_similarity(q_embs, q_embs)
        a_mat = cosine_similarity(a_embs, a_embs)

        results = []
        for i, j in combinations(range(len(self.current_mcqs)), 2):
            q_sim = float(q_mat[i][j])
            a_sim = float(a_mat[i][j])
            tags_i = set(self.current_mcqs[i].get('tags', []) or [])
            tags_j = set(self.current_mcqs[j].get('tags', []) or [])
            overlap = sorted(tags_i.intersection(tags_j))

            final_sim, answer_weight = self._calculate_adaptive_similarity(q_sim, a_sim)

            if final_sim < threshold:
                continue

            results.append({
                'idx1': i,
                'idx2': j,
                'q1': self.current_mcqs[i].get('question', ''),
                'q2': self.current_mcqs[j].get('question', ''),
                'question_sim': round(q_sim, 4),
                'answer_sim': round(a_sim, 4),
                'answer_weight': round(answer_weight, 4),
                'final_sim': round(final_sim, 4),
                'label': self._classify_similarity(final_sim),
                'shared_tags': overlap,
            })

        results.sort(key=lambda x: x['final_sim'], reverse=True)
        return results

    def _run_similarity_check(self):
        """Run and print similarity analysis for currently loaded/tagged MCQs."""
        if len(self.current_mcqs) < 2:
            print("❌ Need at least 2 questions to run similarity check.")
            return

        print("\n🔍 QUESTION SIMILARITY CHECK")
        print("-" * 30)
        try:
            user_threshold = input(f"Threshold (default {CUTOFF_THRESHOLD}): ").strip()
            threshold = float(user_threshold) if user_threshold else CUTOFF_THRESHOLD
        except ValueError:
            print(f"⚠ Invalid threshold. Using default {CUTOFF_THRESHOLD}.")
            threshold = CUTOFF_THRESHOLD

        try:
            results = self._find_similar_tagged_questions(threshold=threshold)
        except Exception as e:
            print(f"❌ Similarity check failed: {e}")
            return

        if not results:
            print(f"✅ No similar pairs found above threshold {threshold}.")
            return

        duplicates = sum(1 for r in results if r['label'] == 'Duplicate')
        highly_similar = sum(1 for r in results if r['label'] == 'Highly Similar')
        similar = sum(1 for r in results if r['label'] == 'Similar')

        print(f"✅ Found {len(results)} similar pairs")
        print(f"   Duplicates: {duplicates} | Highly Similar: {highly_similar} | Similar: {similar}")

        max_show = 10
        for k, r in enumerate(results[:max_show], 1):
            tags_msg = ', '.join(r['shared_tags']) if r['shared_tags'] else 'none'
            print(f"\n{k}. {r['label']} | score={r['final_sim']} | shared_tags={tags_msg}")
            print(f"   Q{r['idx1'] + 1}: {r['q1'][:120]}")
            print(f"   Q{r['idx2'] + 1}: {r['q2'][:120]}")

    def _auto_tag_mcqs(self):
        """Run auto-tagging using Groq LLM hierarchical batch tagger."""
        if not self.current_mcqs:
            print("❌ No MCQs loaded. Use option 7 to upload an MCQ file first.")
            return

        before = sum(1 for q in self.current_mcqs if q.get('main_tag'))
        print("🏷️  Auto-tagging with Groq LLM (hierarchical main_tag + sub_tags)...")
        try:
            # Re-tag all loaded MCQs so output always reflects LLM tagging.
            tagged = self.mcq_generator.auto_tag_questions(self.current_mcqs)
            self.current_mcqs = [self._sync_hierarchical_tag_fields(q) for q in tagged]
        except Exception as e:
            print(f"❌ Auto-tagging failed: {e}")
            return

        after = sum(1 for q in self.current_mcqs if q.get('main_tag'))
        confident = sum(1 for q in self.current_mcqs if q.get('confident'))
        print(f"✅ Tagging complete: {after}/{len(self.current_mcqs)} tagged (was {before}).")
        print(f"🔎 Confident tags: {confident}/{len(self.current_mcqs)}")

        print("🔎 Tagged preview:")
        for i, q in enumerate(self.current_mcqs[:8], 1):
            main_tag = q.get('main_tag', 'General Knowledge')
            sub_tags = q.get('sub_tags', [])
            print(f"   {i}. {main_tag} | {', '.join(sub_tags)}")

    def run(self):
        """Run the main terminal application"""
        self._print_banner()
        
        while True:
            self._show_main_menu()
            choice = input("\n🎯 Enter your choice (0-9): ").strip()

            if choice == "1":
                self._upload_document()
            elif choice == "2":
                self._generate_mcqs()
            elif choice == "3":
                self._view_mcqs()
            elif choice == "4":
                self._refine_mcqs()
            elif choice == "5":
                self._export_mcqs()
            elif choice == "6":
                self._clear_data()
            elif choice == "7":
                self._upload_mcq_file()
            elif choice == "8":
                self._auto_tag_mcqs()
            elif choice == "9":
                self._run_similarity_check()
            elif choice == "0":
                print("\n👋 Goodbye! Thanks for using RAG MCQ Generator!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _print_banner(self):
        """Print application banner"""
        print("\n" + "=" * 60)
        print("🚀 RAG MCQ Generator - Terminal Version")
        print("=" * 60)
        print(f"🤖 Model: {Config.GROQ_MODEL}")
        print(f"📊 Chunk Size: {Config.CHUNK_SIZE}, Overlap: {Config.CHUNK_OVERLAP}")
        print(f"🔄 Retries: {Config.LLM_RETRIES}, Delay: {Config.LLM_RETRY_DELAY}s")
        print("=" * 60)
    
    def _show_main_menu(self):
        """Show main menu options"""
        print("\n📋 MAIN MENU:")
        print("1. 📁 Upload Document")
        print("2. 🎯 Generate MCQs")
        print("3. 👀 View MCQs")
        print("4. 🔄 Refine MCQs")
        print("5. 📤 Export MCQs")
        print("6. 🗑️  Clear Data")
        print("7. 📂 Upload MCQ File (JSON/CSV)")
        print("8. 🏷️  Auto Tag MCQs (Main + Sub Tags)")
        print("9. 🔍 Similarity Check")
        print("0. ❌ Exit")

        if self.document_text:
            print(f"\n📄 Current Document: {len(self.document_text)} characters")
        if self.current_mcqs:
            print(f"🎯 Loaded Questions: {len(self.current_mcqs)}")
    
    def _upload_document(self):
        """Handle document upload"""
        print("\n📁 DOCUMENT UPLOAD")
        print("-" * 30)

        print("Choose input method:")
        print("1. Enter text directly")
        print("2. Provide file path (or just paste the path/filename directly)")

        choice = input("Enter choice (1-2) or file path: ").strip()

        if choice == "1":
            print("\n📝 Enter your text (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)

            # Remove the last empty line
            if lines and lines[-1] == "":
                lines.pop()

            self.document_text = "\n".join(lines)

        elif choice == "2":
            file_path = input("Enter file path: ").strip()
            self._load_file(file_path)

        else:
            # User typed a path/filename directly — treat it as a file path
            self._load_file(choice)
        
        if self.document_text:
            # Process document in RAG system
            try:
                documents = self.rag_system.process_documents(self.document_text)
                self.rag_system.create_vectorstore(documents)
                summary = self.rag_system.get_document_summary()
                print(f"📊 Processed into {summary['total_chunks']} chunks")
            except Exception as e:
                print(f"❌ Error processing document: {e}")
        else:
            print("❌ No document content provided.")

    def _load_file(self, file_path: str):
        """Load a file using DocumentProcessor (supports PDF, DOCX, TXT)"""
        # If no directory given, check current dir and script dir
        if not os.path.dirname(file_path):
            local = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
            if os.path.exists(local):
                file_path = local

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"📂 Loading: {file_path}")
        try:
            text = DocumentProcessor.process_document(file_path)
            if text:
                self.document_text = text
                print(f"✅ File loaded: {len(self.document_text)} characters")
            else:
                print("❌ No text extracted from file.")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    def _generate_mcqs(self):
        """Generate MCQs from document content"""
        if not self.document_text:
            print("❌ No document available. Please upload a document first.")
            return
        
        print("\n🎯 GENERATE MCQs")
        print("-" * 30)
        
        try:
            num_questions = int(input("Number of questions to generate (1-30): "))
            if num_questions < 1 or num_questions > 30:
                print("❌ Invalid number. Using default (10).")
                num_questions = 10
        except ValueError:
            print("❌ Invalid input. Using default (10).")
            num_questions = 10
        
        print(f"🤖 Generating {num_questions} MCQs...")
        
        try:
            # Get context chunks for MCQ generation
            context_chunks = self.rag_system.get_context_for_mcq(num_questions)
            
            # Generate MCQs
            self.current_mcqs = self.mcq_generator.generate_mcqs(
                context_chunks,
                num_questions
            )
            self.current_mcqs = [self._sync_hierarchical_tag_fields(q) for q in self.current_mcqs]
            
            print(f"✅ Generated {len(self.current_mcqs)} MCQs successfully!")
            
        except Exception as e:
            print(f"❌ Error generating MCQs: {str(e)}")
    
    def _view_mcqs(self):
        """View generated MCQs"""
        if not self.current_mcqs:
            print("❌ No MCQs available. Please generate some first.")
            return
        
        print(f"\n👀 VIEWING {len(self.current_mcqs)} MCQs")
        print("=" * 60)
        
        show_answers = input("Show answers? (y/n): ").lower().strip() == 'y'
        
        for i, mcq in enumerate(self.current_mcqs, 1):
            print(f"\n📝 Question {i}:")
            print(f"Q: {mcq.get('question', '')}")

            # Display tags
            main_tag = mcq.get('main_tag') or mcq.get('category', 'general')
            sub_tags = mcq.get('sub_tags', [])
            tags = mcq.get('tags', [])
            difficulty = mcq.get('difficulty', 'medium')
            confident = mcq.get('confident', None)

            if main_tag:
                print(f"🏷️  Main Tag: {main_tag}")
            if sub_tags:
                print(f"   Sub Tags: {', '.join(sub_tags)}")
            elif tags:
                print(f"🏷️  Tags: {', '.join(tags)}")

            if confident is not None:
                print(f"📊 Confidence: {confident} | Difficulty: {difficulty}")
            else:
                print(f"📊 Difficulty: {difficulty}")

            # Options
            options = mcq.get('options', {})
            for option, text in options.items():
                print(f"   {option}. {text}")

            # Answer and explanation (if showing answers)
            if show_answers:
                print(f"✅ Correct Answer: {mcq.get('correct_answer', '')}")
                print(f"💡 Explanation: {mcq.get('explanation', '')}")

            print("-" * 40)
    
    def _refine_mcqs(self):
        """Refine MCQs based on user feedback"""
        if not self.current_mcqs:
            print("❌ No MCQs available. Please generate some first.")
            return
        
        print("\n🔄 REFINE MCQs")
        print("-" * 30)
        
        feedback = input("What would you like to improve? (e.g., make easier, more challenging, clearer): ")
        
        if feedback.strip():
            print("🔄 Refining questions...")
            try:
                refined_mcqs = self.mcq_generator.refine_mcqs(self.current_mcqs, feedback)
                
                if refined_mcqs:
                    self.current_mcqs = [self._sync_hierarchical_tag_fields(q) for q in refined_mcqs]
                    print("✅ Questions refined successfully!")
                else:
                    print("⚠️  No changes made to questions.")
                    
            except Exception as e:
                print(f"❌ Error refining questions: {str(e)}")
        else:
            print("❌ No feedback provided.")
    
    def _export_mcqs(self):
        """Export MCQs to different formats"""
        if not self.current_mcqs:
            print("❌ No MCQs available. Please generate some first.")
            return
        
        print("\n📤 EXPORT MCQs")
        print("-" * 30)
        print("1. Export to JSON file")
        print("2. Export to CSV file")
        print("3. Display formatted text")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            filename = input("Enter filename (default: mcqs.json): ").strip() or "mcqs.json"
            try:
                formatted_mcqs = []
                for mcq in self.current_mcqs:
                    out = dict(mcq)
                    out.pop('category', None)
                    out.pop('tags', None)
                    formatted_mcqs.append(out)

                json_data = {"mcqs": formatted_mcqs}
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print(f"✅ MCQs exported to {filename}")
            except Exception as e:
                print(f"❌ Error exporting: {e}")
        
        elif choice == "2":
            filename = input("Enter filename (default: mcqs.csv): ").strip() or "mcqs.csv"
            try:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer', 'Explanation'])
                    
                    for mcq in self.current_mcqs:
                        options = mcq.get('options', {})
                        writer.writerow([
                            mcq.get('question', ''),
                            options.get('A', ''),
                            options.get('B', ''),
                            options.get('C', ''),
                            options.get('D', ''),
                            mcq.get('correct_answer', ''),
                            mcq.get('explanation', '')
                        ])
                print(f"✅ MCQs exported to {filename}")
            except Exception as e:
                print(f"❌ Error exporting: {e}")
        
        elif choice == "3":
            print("\n📋 FORMATTED MCQs:")
            print("=" * 60)
            for i, mcq in enumerate(self.current_mcqs, 1):
                print(f"\nQuestion {i}: {mcq.get('question', '')}")
                options = mcq.get('options', {})
                for option, text in options.items():
                    print(f"{option}. {text}")
                print(f"Correct Answer: {mcq.get('correct_answer', '')}")
                print(f"Explanation: {mcq.get('explanation', '')}")
                print("-" * 40)
        
        else:
            print("❌ Invalid choice.")
    
    def _clear_data(self):
        """Clear all data and reset the application"""
        print("\n🗑️  CLEAR DATA")
        print("-" * 30)
        confirm = input("Are you sure you want to clear all data? (y/n): ").lower().strip()
        if confirm == 'y':
            self.current_mcqs = []
            self.document_text = ""
            if self.rag_system:
                self.rag_system.clear_vectorstore()
            print("✅ All data cleared successfully!")
        else:
            print("❌ Operation cancelled.")

    # ─────────────────────────────────────────────
    #  NEW: Upload an existing MCQ file
    # ─────────────────────────────────────────────
    def _normalize_mcq(self, raw: dict) -> dict:
        """Normalize any MCQ dict shape into the terminal app's standard MCQ structure."""
        mcq = {}

        # Question text
        mcq["question"] = raw.get("question") or raw.get("Question") or ""

        # Options — handle list OR dict
        opts = raw.get("options") or raw.get("Options") or []
        if isinstance(opts, list):
            keys = ["A", "B", "C", "D"]
            mcq["options"] = {keys[i]: v for i, v in enumerate(opts) if i < 4}
        elif isinstance(opts, dict):
            mcq["options"] = opts
        else:
            mcq["options"] = {}

        # Correct answer
        mcq["correct_answer"] = (
            raw.get("correct_answer") or raw.get("answer") or
            raw.get("Correct Answer") or ""
        )

        # Explanation
        mcq["explanation"] = raw.get("explanation") or raw.get("Explanation") or ""

        # Preserve existing tags/category if present
        for key in ("tags", "category", "main_tag", "sub_tags", "confident", "difficulty", "bloom_category", "topic", "id", "key_concepts"):
            if key in raw:
                mcq[key] = raw[key]

        mcq = self._sync_hierarchical_tag_fields(mcq)

        return mcq

    def _fast_tag_untagged_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tag only untagged questions using local ML tagger (fast, no API calls)."""
        untagged_indices = [i for i, q in enumerate(questions) if not q.get('tags')]
        if not untagged_indices:
            return questions

        untagged_batch = [questions[i] for i in untagged_indices]
        print(f"🏷️  Fast-tagging {len(untagged_batch)} question(s) with local model...")
        tagged_batch = self.mcq_generator.tag_questions(untagged_batch)

        for idx, tagged_q in zip(untagged_indices, tagged_batch):
            questions[idx].update({
                'tags': tagged_q.get('tags', questions[idx].get('tags', ['general'])),
                'category': tagged_q.get('category', questions[idx].get('category', 'general')),
                'difficulty': tagged_q.get('difficulty', questions[idx].get('difficulty', 'medium')),
                'bloom_category': tagged_q.get('bloom_category', questions[idx].get('bloom_category', 'understand')),
                'key_concepts': tagged_q.get('key_concepts', questions[idx].get('key_concepts', [])),
            })

        return questions

    def _upload_mcq_file(self):
        """Load an MCQ file in any format and normalize it (no auto-tag/similarity)."""
        print("\n📂 UPLOAD MCQ FILE")
        print("-" * 30)
        file_path = input("Enter file path: ").strip()

        # Resolve bare filename relative to script directory
        if not os.path.dirname(file_path):
            local = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
            if os.path.exists(local):
                file_path = local

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        raw_mcqs = []

        # Try JSON first regardless of file extension
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                raw_mcqs = data
            elif isinstance(data, dict):
                # Accept any key that holds a list
                for key in ("mcqs", "questions", "data", "items"):
                    if key in data and isinstance(data[key], list):
                        raw_mcqs = data[key]
                        break
                if not raw_mcqs:
                    # Last resort: first list value found
                    for v in data.values():
                        if isinstance(v, list):
                            raw_mcqs = v
                            break

        except (json.JSONDecodeError, ValueError):
            # Not JSON — try CSV
            try:
                import csv
                with open(file_path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        raw_mcqs.append(dict(row))
            except Exception as e:
                print(f"❌ Could not parse file as JSON or CSV: {e}")
                return
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return

        if not raw_mcqs:
            print("❌ No questions found in file.")
            return

        # Normalize every MCQ into standard shape
        mcqs = [self._normalize_mcq(r) for r in raw_mcqs]
        mcqs = [m for m in mcqs if m.get("question")]   # drop empties

        print(f"✅ Loaded {len(mcqs)} questions from '{os.path.basename(file_path)}'")

        self.current_mcqs = mcqs
        tagged = sum(1 for q in mcqs if q.get('main_tag') or q.get('category') or q.get('tags'))
        print(f"🏷️  Existing tags in file: {tagged}/{len(mcqs)}")
        print("💡 Next: option 8 for auto-tagging (main + sub tags), then option 9 for similarity check.")


def main():
    """Main function to run the terminal application"""
    try:
        app = TerminalMCQApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
