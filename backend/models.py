"""
Pydantic models for API request/response validation
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MCQOption(BaseModel):
    """MCQ options"""
    A: str
    B: str
    C: str
    D: str


class MCQ(BaseModel):
    """Single MCQ structure"""
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str = ""
    main_tag: Optional[str] = None
    sub_tags: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    category: Optional[str] = None
    difficulty: Optional[str] = "medium"
    confident: Optional[bool] = None
    bloom_category: Optional[str] = None
    key_concepts: Optional[List[str]] = []
    topic: Optional[str] = None
    id: Optional[str] = None


class DocumentUploadRequest(BaseModel):
    """Request for document text upload"""
    text: str = Field(..., min_length=10)


class GenerateMCQRequest(BaseModel):
    """Request to generate MCQs"""
    num_questions: int = Field(default=10, ge=1, le=30)


class RefineMCQRequest(BaseModel):
    """Request to refine MCQs"""
    mcqs: List[MCQ]
    feedback: str = Field(..., min_length=3)


class AutoTagRequest(BaseModel):
    """Request to auto-tag MCQs"""
    mcqs: List[MCQ]


class SimilarityCheckRequest(BaseModel):
    """Request to check similarity"""
    mcqs: List[MCQ]
    threshold: float = Field(default=0.75, ge=0.0, le=1.0)


class SimilarityPair(BaseModel):
    """Similar question pair"""
    idx1: int
    idx2: int
    q1: str
    q2: str
    question_sim: float
    answer_sim: float
    answer_weight: float
    final_sim: float
    label: str
    shared_tags: List[str]


class SimilarityCheckResponse(BaseModel):
    """Response from similarity check"""
    total_pairs: int
    similar_pairs: List[SimilarityPair]
    duplicates: int
    highly_similar: int
    similar: int


class ExportFormat(BaseModel):
    """Export format request"""
    mcqs: List[MCQ]
    format: str = Field(default="json", pattern="^(json|csv)$")


class DocumentSummary(BaseModel):
    """Document processing summary"""
    total_chunks: int
    total_characters: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    rag_system: bool
    mcq_generator: bool
    similarity_model: bool
