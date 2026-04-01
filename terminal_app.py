#!/usr/bin/env python3
"""
Terminal-based RAG MCQ Generator
Run this directly in the terminal without Streamlit
"""

import os
import sys
from typing import List, Dict, Any
import json

from document_processor import DocumentProcessor
from rag_system import RAGSystem
from mcq_generator import MCQGenerator
from config import Config
from question_tagger import QuestionTagger

class TerminalMCQApp:
    """Terminal-based MCQ Generation Application"""
    
    def __init__(self):
        self.rag_system = None
        self.mcq_generator = None
        self.tagger = QuestionTagger()
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
    
    def run(self):
        """Run the main terminal application"""
        self._print_banner()
        
        while True:
            self._show_main_menu()
            choice = input("\n🎯 Enter your choice (1-9): ").strip()

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
                self._manual_tag_mcqs()
            elif choice == "9":
                self._compare_tags()
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
        print("8. 🏷️  Manual Tag MCQs")
        print("9. 📊 Compare Tags with Ground Truth")
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

            # Display hierarchical tags
            main_tag = mcq.get('main_tag')
            sub_tags = mcq.get('sub_tags', [])
            difficulty = mcq.get('difficulty', 'medium')

            if main_tag:
                print(f"🎯 Main Category: {main_tag}")
            if sub_tags:
                print(f"🏷️  Sub-Tags: {', '.join(sub_tags)}")

            print(f"📊 Difficulty: {difficulty}")
            
            intent = mcq.get('intent')
            if intent:
                print(f"🧠 Intent: {intent}")

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
                    self.current_mcqs = refined_mcqs
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
        print("4. Export to Excel (.xlsx) file")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            filename = input("Enter filename (default: mcqs.json): ").strip() or "mcqs.json"
            try:
                json_data = {"mcqs": self.current_mcqs}
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
                
        elif choice == "4":
            filename = input("Enter filename (default: mcqs.xlsx): ").strip() or "mcqs.xlsx"
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            try:
                import pandas as pd
                rows = []
                for mcq in self.current_mcqs:
                    options = mcq.get('options', {})
                    row = {
                        'Question': mcq.get('question', ''),
                        'Option A': options.get('A', ''),
                        'Option B': options.get('B', ''),
                        'Option C': options.get('C', ''),
                        'Option D': options.get('D', ''),
                        'Correct Answer': mcq.get('correct_answer', ''),
                        'Explanation': mcq.get('explanation', ''),
                        'Intent': mcq.get('intent', ''),
                        'Tags': ', '.join(mcq.get('tags', []))
                    }
                    rows.append(row)
                df = pd.DataFrame(rows)
                df.to_excel(filename, index=False)
                print(f"✅ MCQs exported to {filename}")
            except ImportError:
                print("❌ pandas or openpyxl missing. Run: conda run -n rag_mcq pip install pandas openpyxl")
            except Exception as e:
                print(f"❌ Error exporting to Excel: {e}")
        
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
        """Normalize any MCQ dict shape into standard {question, options{A-D}, correct_answer, explanation}"""
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
        for key in ("tags", "category", "difficulty", "bloom_category", "topic", "id"):
            if key in raw:
                mcq[key] = raw[key]

        return mcq

    def _upload_mcq_file(self):
        """Load an MCQ file in any format, normalize it, then auto-tag untagged questions"""
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

        # Use LLM to tag every question (question text + correct answer only)
        mcqs = self.mcq_generator.llm_tag_questions(mcqs)

        self.current_mcqs = mcqs
        tagged      = sum(1 for q in mcqs if q.get('tags'))
        needs_input = sum(1 for q in mcqs if not q.get('tags'))
        print(f"✅ {tagged}/{len(mcqs)} tagged by LLM.")
        if needs_input:
            print(f"⚠️  {needs_input} question(s) the LLM couldn't tag — use option 8 to fill them in.")
        else:
            print("💡 All tagged! Use option 3 to view  |  option 5 to export.")


    def _manual_tag_mcqs(self):
        """
        Manual tagging for questions the LLM couldn't tag (needs_review=True / empty tags).
        Shows question text + correct answer for each, lets user type tags.
        """
        if not self.current_mcqs:
            print("❌ No MCQs loaded. Use option 7 to upload an MCQ file first.")
            return

        # Find questions that need review
        needs_review = [q for q in self.current_mcqs if q.get('needs_review') or not q.get('tags')]
        total = len(self.current_mcqs)

        print(f"\n🏷️  MANUAL TAGGING  —  {len(needs_review)}/{total} question(s) need your input")
        print("═" * 60)

        if not needs_review:
            print("✅ All questions are already tagged by the LLM.")
            override = input("Tag ALL questions manually instead? (y/n, default n): ").strip().lower()
            if override != 'y':
                print("💡 Use option 5 to export  |  option 3 to view.")
                return
            needs_review = self.current_mcqs

        print("For each question:")
        print("  • Type your tags (comma-separated)  —  e.g. 'sql, select statement'")
        print("  • Press Enter to leave as-is and skip")
        print("  • Type 'q' to quit early\n")

        changed = 0

        for i, mcq in enumerate(needs_review, 1):
            q_text   = mcq.get('question', '(no text)')
            # Resolve correct answer text from options dict
            options  = mcq.get('options', {})
            ans_key  = mcq.get('correct_answer', '?')
            if isinstance(options, dict):
                ans_text = next(
                    (v for k, v in options.items()
                     if str(k).strip().upper() == str(ans_key).strip().upper()),
                    str(ans_key)
                )
            else:
                ans_text = str(ans_key)

            existing = ', '.join(mcq.get('tags', [])) or '— (empty)'
            auto_tags = mcq.get('tags', [])
            auto_diff = mcq.get('difficulty', 'medium')
            auto_bloom = mcq.get('bloom_category', 'understand')

            print(f"\n{'═'*60}")
            print(f"Q {i}/{len(needs_review)}  {'⚠️  (LLM unsure)' if mcq.get('needs_review') else '✅ (LLM tagged)'}")
            print(f"Q: {q_text}")
            print(f"✔ Correct answer: {ans_text}")
            print(f"   Current tags: {existing}")

            # ── Tags ──────────────────────────────────────────────
            tag_input = input("\nYour tags (comma-separated, or Enter to skip): ").strip()
            if tag_input.lower() == 'q':
                print("⏹ Stopped.")
                break
            if tag_input:
                tags = [t.strip() for t in tag_input.split(',') if t.strip()]
                mcq['tags'] = tags      # only the tags field is updated
                changed += 1

            final_tags = ', '.join(mcq.get('tags', [])) or '— (still empty)'
            print(f"   ✅ Saved — tags: {final_tags}")

        print(f"\n{'═'*60}")
        print(f"🏷️  Done — {changed} question(s) manually tagged.")
        still_empty = sum(1 for q in self.current_mcqs if not q.get('tags'))
        if still_empty:
            print(f"⚠️  {still_empty} question(s) still have no tags.")
        print("💡 Use option 9 to compare  |  option 5 to export  |  option 3 to view.")


    def _compare_tags(self):
        """
        Compare LLM-generated tags on loaded questions against a ground-truth JSON.

        Ground-truth JSON format:
          [{"question_number": 1, "tag": "Science"}, ...]

        Matching is done by question index (question_number 1 = first loaded MCQ).
        """
        if not self.current_mcqs:
            print("❌ No MCQs loaded. Upload a file first (option 7).")
            return

        print("\n📊 COMPARE TAGS WITH GROUND TRUTH")
        print("═" * 60)
        gt_path = input("Enter ground-truth JSON file path: ").strip()

        # Resolve bare filename
        if not os.path.dirname(gt_path):
            local = os.path.join(os.path.dirname(os.path.abspath(__file__)), gt_path)
            if os.path.exists(local):
                gt_path = local

        if not os.path.exists(gt_path):
            print(f"❌ File not found: {gt_path}")
            return

        try:
            with open(gt_path, encoding='utf-8') as f:
                gt_data = json.load(f)
        except Exception as e:
            print(f"❌ Could not read file: {e}")
            return

        # Build {question_number: tag} map
        if not isinstance(gt_data, list):
            print("❌ Ground-truth JSON must be a list of {question_number, tag} objects.")
            return

        gt_map = {}
        for entry in gt_data:
            num = entry.get('question_number') or entry.get('id')
            tag = entry.get('tag') or entry.get('tags') or ""
            if isinstance(tag, list):
                tag = tag[0] if tag else ""
            if num:
                gt_map[int(num)] = str(tag).strip()

        print(f"\n{'No':>4}  {'LLM Tag':<30}  {'Correct Tag':<30}  Match")
        print("-" * 72)

        match_count  = 0
        total_compared = 0

        for i, mcq in enumerate(self.current_mcqs, start=1):
            correct_tag = gt_map.get(i, "(not in ground truth)")
            if correct_tag == "(not in ground truth)":
                continue

            llm_tags = mcq.get('tags', [])
            llm_tag  = ', '.join(llm_tags) if llm_tags else '(empty)'

            # Case-insensitive match on any of the LLM tags
            matched = any(
                t.strip().lower() == correct_tag.lower()
                for t in llm_tags
            )
            if matched:
                match_count += 1

            icon = "✅" if matched else "❌"
            total_compared += 1
            print(f"{i:>4}  {llm_tag:<30}  {correct_tag:<30}  {icon}")

        print("-" * 72)
        if total_compared:
            pct = 100 * match_count / total_compared
            print(f"\n🎯 Accuracy: {match_count}/{total_compared} ({pct:.1f}%)")
            wrong = total_compared - match_count
            if wrong:
                print(f"⚠️  {wrong} mismatches — use option 8 to fix, then option 5 to export.")
            else:
                print("🎉 All tags match!")
        else:
            print("⚠️  No overlap between loaded questions and ground-truth numbers.")


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
