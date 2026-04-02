"""
FastAPI Backend for RAG MCQ Generator
Integrates all terminal_app.py functionality with REST API
"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from io import StringIO
from itertools import combinations

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from document_processor import DocumentProcessor
    from rag_system import RAGSystem
    from mcq_generator import MCQGenerator
    from config import Config
    from backend.models import *
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"Python path: {sys.path}")
    raise

# Configuration
SIMILARITY_MODEL_PATH = os.getenv('MODEL_PATH', '/Users/k/rag_questions/similiarty /mcq_intent_model')
CUTOFF_THRESHOLD = 0.75
DUPLICATE_THRESHOLD = 0.90
HIGH_SIMILARITY_THRESHOLD = 0.80

app = FastAPI(
    title="RAG MCQ Generator API",
    description="Generate and manage MCQs using RAG with LLM",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_system: RAGSystem = None
mcq_generator: MCQGenerator = None
similarity_model: SentenceTransformer = None
current_document_text: str = ""
current_mcqs: List[Dict[str, Any]] = []


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global rag_system, mcq_generator

    print("🚀 Initializing RAG MCQ Generator...")

    try:
        print("📚 Initializing RAG System...")
        rag_system = RAGSystem()

        print("🤖 Initializing MCQ Generator...")
        mcq_generator = MCQGenerator()

        print("✅ All components initialized successfully!")

    except Exception as e:
        print(f"❌ Error initializing components: {str(e)}")
        raise


def _load_similarity_model():
    """Load fine-tuned similarity model"""
    global similarity_model

    if similarity_model is not None:
        return similarity_model

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
            f"'{SIMILARITY_MODEL_PATH}'."
        )

    print(f"🧠 Loading similarity model from: {SIMILARITY_MODEL_PATH}")
    try:
        similarity_model = SentenceTransformer(SIMILARITY_MODEL_PATH)
        print("✅ Similarity model loaded")
    except Exception as e:
        raise RuntimeError(
            f"Could not load fine-tuned similarity model: {e}"
        )

    return similarity_model


def _resolve_answer_text(mcq: Dict[str, Any]) -> str:
    """Resolve answer text from MCQ"""
    answer = str(mcq.get('correct_answer', '')).strip()
    options = mcq.get('options', {}) or {}

    if isinstance(options, dict) and answer in options:
        return str(options.get(answer, '')).strip()

    return answer


def _sync_hierarchical_tag_fields(mcq: Dict[str, Any]) -> Dict[str, Any]:
    """Sync hierarchical tag fields"""
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


def _calculate_adaptive_similarity(q_sim: float, a_sim: float):
    """Calculate adaptive similarity"""
    answer_weight = 0.15 + 0.70 * (1.0 - q_sim)
    question_weight = 1.0 - answer_weight
    final_sim = answer_weight * a_sim + question_weight * q_sim
    return final_sim, answer_weight


def _classify_similarity(sim_score: float) -> str:
    """Classify similarity level"""
    if sim_score >= DUPLICATE_THRESHOLD:
        return 'Duplicate'
    if sim_score >= HIGH_SIMILARITY_THRESHOLD:
        return 'Highly Similar'
    if sim_score >= CUTOFF_THRESHOLD:
        return 'Similar'
    return 'Different'


# ==================== API ENDPOINTS ====================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "RAG MCQ Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        rag_system=rag_system is not None,
        mcq_generator=mcq_generator is not None,
        similarity_model=similarity_model is not None
    )


@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "groq_model": Config.GROQ_MODEL,
        "chunk_size": Config.CHUNK_SIZE,
        "chunk_overlap": Config.CHUNK_OVERLAP,
        "llm_retries": Config.LLM_RETRIES,
        "llm_retry_delay": Config.LLM_RETRY_DELAY,
        "similarity_model": SIMILARITY_MODEL_PATH,
        "cutoff_threshold": CUTOFF_THRESHOLD,
        "duplicate_threshold": DUPLICATE_THRESHOLD,
        "high_similarity_threshold": HIGH_SIMILARITY_THRESHOLD
    }


@app.post("/upload-text")
async def upload_text(request: DocumentUploadRequest):
    """Upload document text"""
    global current_document_text

    try:
        current_document_text = request.text

        # Process document in RAG system
        documents = rag_system.process_documents(current_document_text)
        rag_system.create_vectorstore(documents)
        summary = rag_system.get_document_summary()

        return {
            "success": True,
            "message": "Document processed successfully",
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload document file (PDF, DOCX, TXT)"""
    global current_document_text

    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process document
        text = DocumentProcessor.process_document(temp_path)

        # Clean up temp file
        os.remove(temp_path)

        if not text:
            raise HTTPException(status_code=400, detail="No text extracted from file")

        current_document_text = text

        # Process in RAG system
        documents = rag_system.process_documents(current_document_text)
        rag_system.create_vectorstore(documents)
        summary = rag_system.get_document_summary()

        return {
            "success": True,
            "message": f"File '{file.filename}' processed successfully",
            "summary": summary,
            "text_length": len(text)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-mcqs")
async def generate_mcqs(request: GenerateMCQRequest):
    """Generate MCQs from uploaded document"""
    global current_mcqs

    if not current_document_text:
        raise HTTPException(status_code=400, detail="No document uploaded. Please upload a document first.")

    try:
        # Get context chunks for MCQ generation
        context_chunks = rag_system.get_context_for_mcq(request.num_questions)

        # Generate MCQs
        mcqs = mcq_generator.generate_mcqs(context_chunks, request.num_questions)
        current_mcqs = [_sync_hierarchical_tag_fields(q) for q in mcqs]

        return {
            "success": True,
            "message": f"Generated {len(current_mcqs)} MCQs successfully",
            "mcqs": current_mcqs,
            "count": len(current_mcqs)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcqs")
async def get_mcqs():
    """Get current MCQs"""
    return {
        "success": True,
        "mcqs": current_mcqs,
        "count": len(current_mcqs)
    }


@app.post("/auto-tag")
async def auto_tag_mcqs(request: AutoTagRequest):
    """Auto-tag MCQs using Groq LLM"""
    global current_mcqs

    if not request.mcqs:
        raise HTTPException(status_code=400, detail="No MCQs provided")

    try:
        # Convert Pydantic models to dicts
        mcqs_dicts = [mcq.dict() if hasattr(mcq, 'dict') else mcq for mcq in request.mcqs]

        print(f"🏷️  Auto-tagging {len(mcqs_dicts)} MCQs...")

        # Re-tag all MCQs
        tagged = mcq_generator.auto_tag_questions(mcqs_dicts)
        tagged_mcqs = [_sync_hierarchical_tag_fields(q) for q in tagged]

        # Update current MCQs if they match
        if len(current_mcqs) == len(tagged_mcqs):
            current_mcqs = tagged_mcqs

        after = sum(1 for q in tagged_mcqs if q.get('main_tag'))
        confident = sum(1 for q in tagged_mcqs if q.get('confident'))

        print(f"✅ Tagged {after}/{len(tagged_mcqs)} MCQs (confident: {confident})")

        return {
            "success": True,
            "message": "MCQs tagged successfully",
            "mcqs": tagged_mcqs,
            "stats": {
                "total": len(tagged_mcqs),
                "tagged": after,
                "confident": confident
            }
        }

    except Exception as e:
        print(f"❌ Auto-tag failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similarity-check", response_model=SimilarityCheckResponse)
async def similarity_check(request: SimilarityCheckRequest):
    """Check similarity between MCQs"""

    if len(request.mcqs) < 2:
        raise HTTPException(status_code=400, detail="At least 2 MCQs required for similarity check")

    try:
        print(f"🔍 Checking similarity for {len(request.mcqs)} MCQs (threshold: {request.threshold})")

        model = _load_similarity_model()

        # Convert Pydantic models to dicts for processing
        mcqs_dicts = [mcq.dict() if hasattr(mcq, 'dict') else mcq for mcq in request.mcqs]

        questions = [str(q.get('question', '')).strip() for q in mcqs_dicts]
        answers = [_resolve_answer_text(q) for q in mcqs_dicts]

        q_embs = model.encode(questions, batch_size=128, normalize_embeddings=True)
        a_embs = model.encode(answers, batch_size=128, normalize_embeddings=True)

        q_mat = cosine_similarity(q_embs, q_embs)
        a_mat = cosine_similarity(a_embs, a_embs)

        results = []
        for i, j in combinations(range(len(mcqs_dicts)), 2):
            q_sim = float(q_mat[i][j])
            a_sim = float(a_mat[i][j])

            tags_i = set(mcqs_dicts[i].get('tags', []) or [])
            tags_j = set(mcqs_dicts[j].get('tags', []) or [])
            overlap = sorted(tags_i.intersection(tags_j))

            final_sim, answer_weight = _calculate_adaptive_similarity(q_sim, a_sim)

            if final_sim < request.threshold:
                continue

            results.append(SimilarityPair(
                idx1=i,
                idx2=j,
                q1=mcqs_dicts[i].get('question', ''),
                q2=mcqs_dicts[j].get('question', ''),
                question_sim=round(q_sim, 4),
                answer_sim=round(a_sim, 4),
                answer_weight=round(answer_weight, 4),
                final_sim=round(final_sim, 4),
                label=_classify_similarity(final_sim),
                shared_tags=overlap
            ))

        results.sort(key=lambda x: x.final_sim, reverse=True)

        duplicates = sum(1 for r in results if r.label == 'Duplicate')
        highly_similar = sum(1 for r in results if r.label == 'Highly Similar')
        similar = sum(1 for r in results if r.label == 'Similar')

        print(f"✅ Found {len(results)} similar pairs (duplicates: {duplicates}, highly similar: {highly_similar})")

        return SimilarityCheckResponse(
            total_pairs=len(results),
            similar_pairs=results,
            duplicates=duplicates,
            highly_similar=highly_similar,
            similar=similar
        )

    except Exception as e:
        print(f"❌ Similarity check failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refine-mcqs")
async def refine_mcqs(request: RefineMCQRequest):
    """Refine MCQs based on feedback"""
    global current_mcqs

    if not request.mcqs:
        raise HTTPException(status_code=400, detail="No MCQs provided")

    try:
        # Convert Pydantic models to dicts
        mcqs_dicts = [q.dict() if hasattr(q, 'dict') else q for q in request.mcqs]

        print(f"🔄 Refining {len(mcqs_dicts)} MCQs with feedback: {request.feedback[:50]}...")

        refined_mcqs = mcq_generator.refine_mcqs(mcqs_dicts, request.feedback)

        if refined_mcqs:
            refined_mcqs = [_sync_hierarchical_tag_fields(q) for q in refined_mcqs]

            # Update current MCQs if they match
            if len(current_mcqs) == len(refined_mcqs):
                current_mcqs = refined_mcqs

            print(f"✅ MCQs refined successfully")

            return {
                "success": True,
                "message": "MCQs refined successfully",
                "mcqs": refined_mcqs
            }
        else:
            print(f"⚠️  No changes made to MCQs")
            return {
                "success": False,
                "message": "No changes made to MCQs",
                "mcqs": mcqs_dicts
            }

    except Exception as e:
        print(f"❌ Refine failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-mcq-file")
async def upload_mcq_file(file: UploadFile = File(...)):
    """Upload existing MCQ file (JSON or CSV)"""
    global current_mcqs

    print(f"📂 Received file: {file.filename}, Content-Type: {file.content_type}")

    try:
        content = await file.read()
        print(f"📊 File size: {len(content)} bytes")

        raw_mcqs = []

        # Try JSON first
        try:
            data = json.loads(content.decode('utf-8'))
            print(f"✅ Successfully parsed as JSON")

            if isinstance(data, list):
                raw_mcqs = data
                print(f"📋 Found list with {len(raw_mcqs)} items")
            elif isinstance(data, dict):
                for key in ("mcqs", "questions", "data", "items"):
                    if key in data and isinstance(data[key], list):
                        raw_mcqs = data[key]
                        print(f"📋 Found key '{key}' with {len(raw_mcqs)} items")
                        break
                if not raw_mcqs:
                    for v in data.values():
                        if isinstance(v, list):
                            raw_mcqs = v
                            print(f"📋 Found list value with {len(raw_mcqs)} items")
                            break

        except (json.JSONDecodeError, ValueError) as je:
            print(f"⚠️  JSON parsing failed: {je}")
            # Try CSV
            try:
                csv_content = content.decode('utf-8')
                reader = csv.DictReader(StringIO(csv_content))
                for row in reader:
                    raw_mcqs.append(dict(row))
                print(f"✅ Successfully parsed as CSV with {len(raw_mcqs)} rows")
            except Exception as e:
                print(f"❌ CSV parsing failed: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not parse file as JSON or CSV: {str(e)}"
                )

        if not raw_mcqs:
            print("❌ No questions found in file")
            raise HTTPException(status_code=400, detail="No questions found in file")

        print(f"🔄 Normalizing {len(raw_mcqs)} MCQs...")

        # Normalize MCQs
        mcqs = []
        for idx, raw in enumerate(raw_mcqs):
            try:
                mcq = _normalize_mcq(raw)
                if mcq.get("question"):
                    mcqs.append(mcq)
            except Exception as e:
                print(f"⚠️  Failed to normalize MCQ {idx}: {e}")
                continue

        print(f"✅ Normalized {len(mcqs)} MCQs successfully")

        current_mcqs = mcqs
        tagged = sum(1 for q in mcqs if q.get('main_tag') or q.get('category') or q.get('tags'))

        return {
            "success": True,
            "message": f"Loaded {len(mcqs)} questions from '{file.filename}'",
            "mcqs": mcqs,
            "count": len(mcqs),
            "tagged": tagged
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _normalize_mcq(raw: dict) -> dict:
    """Normalize any MCQ dict shape"""
    mcq = {}

    # Question text
    mcq["question"] = raw.get("question") or raw.get("Question") or ""

    # Options
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

    # Preserve existing tags/category
    for key in ("tags", "category", "main_tag", "sub_tags", "confident",
                "difficulty", "bloom_category", "topic", "id", "key_concepts"):
        if key in raw:
            mcq[key] = raw[key]

    mcq = _sync_hierarchical_tag_fields(mcq)

    return mcq


@app.post("/export")
async def export_mcqs(request: ExportFormat):
    """Export MCQs to JSON or CSV"""

    if not request.mcqs:
        raise HTTPException(status_code=400, detail="No MCQs to export")

    try:
        if request.format == "json":
            # Format MCQs for export
            formatted_mcqs = []
            for mcq in request.mcqs:
                mcq_dict = mcq.dict() if hasattr(mcq, 'dict') else mcq
                out = dict(mcq_dict)
                out.pop('category', None)
                out.pop('tags', None)
                formatted_mcqs.append(out)

            json_data = {"mcqs": formatted_mcqs}
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

            return StreamingResponse(
                iter([json_str]),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=mcqs.json"}
            )

        elif request.format == "csv":
            # Create CSV
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Question', 'Option A', 'Option B', 'Option C', 'Option D',
                           'Correct Answer', 'Explanation', 'Main Tag', 'Sub Tags'])

            for mcq in request.mcqs:
                mcq_dict = mcq.dict() if hasattr(mcq, 'dict') else mcq
                options = mcq_dict.get('options', {})
                sub_tags = mcq_dict.get('sub_tags', [])
                sub_tags_str = ', '.join(sub_tags) if isinstance(sub_tags, list) else str(sub_tags)

                writer.writerow([
                    mcq_dict.get('question', ''),
                    options.get('A', ''),
                    options.get('B', ''),
                    options.get('C', ''),
                    options.get('D', ''),
                    mcq_dict.get('correct_answer', ''),
                    mcq_dict.get('explanation', ''),
                    mcq_dict.get('main_tag', ''),
                    sub_tags_str
                ])

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=mcqs.csv"}
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'csv'")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear")
async def clear_data():
    """Clear all data"""
    global current_document_text, current_mcqs

    try:
        current_document_text = ""
        current_mcqs = []

        if rag_system:
            rag_system.clear_vectorstore()

        return {
            "success": True,
            "message": "All data cleared successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('PORT', 8000))

    print(f"\n{'='*60}")
    print(f"🚀 RAG MCQ Generator API")
    print(f"{'='*60}")
    print(f"🤖 Model: {Config.GROQ_MODEL}")
    print(f"📊 Chunk Size: {Config.CHUNK_SIZE}, Overlap: {Config.CHUNK_OVERLAP}")
    print(f"🔄 Retries: {Config.LLM_RETRIES}, Delay: {Config.LLM_RETRY_DELAY}s")
    print(f"🌐 Port: {port}")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"{'='*60}\n")

    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
