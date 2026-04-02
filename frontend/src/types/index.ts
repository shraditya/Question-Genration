// Type definitions for RAG MCQ Generator

export interface MCQOption {
  A: string;
  B: string;
  C: string;
  D: string;
}

export interface MCQ {
  id?: string;
  question: string;
  options: MCQOption | Record<string, string>;
  correct_answer: string;
  explanation?: string;
  main_tag?: string;
  sub_tags?: string[];
  tags?: string[];
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  confident?: boolean | null;
  confidence?: number; // 0-100
  bloom_category?: string;
  key_concepts?: string[];
  topic?: string;
  created_at?: string;
  source?: string;
}

export interface SimilarityPair {
  idx1: number;
  idx2: number;
  q1: string;
  q2: string;
  question_sim: number;
  answer_sim: number;
  answer_weight: number;
  final_sim: number;
  label: 'Duplicate' | 'Highly Similar' | 'Similar' | 'Different';
  shared_tags: string[];
}

export interface TagStatistics {
  total: number;
  tagged: number;
  confident: number;
  needsReview: number;
}

export interface TagDistribution {
  [tag: string]: number;
}

export interface ConfidenceRange {
  range: string;
  count: number;
  percentage: number;
}

export interface ExportConfig {
  format: 'json' | 'csv' | 'moodle' | 'qti';
  includeAll: boolean;
  onlyTagged: boolean;
  onlyHighConfidence: boolean;
  onlyUnique: boolean;
  includeTags: boolean;
  includeConfidence: boolean;
  includeExplanations: boolean;
  includeMetadata: boolean;
}

export interface DashboardStats {
  totalMCQs: number;
  documentsProcessed: number;
  tagCoverage: number;
  duplicateRate: number;
}

export interface Activity {
  id: string;
  type: 'generate' | 'tag' | 'duplicate' | 'export';
  description: string;
  timestamp: string;
  count?: number;
}

export interface SystemHealth {
  status: string;
  rag_system: boolean;
  mcq_generator: boolean;
  similarity_model: boolean;
}

export interface SystemConfig {
  groq_model: string;
  chunk_size: number;
  chunk_overlap: number;
  llm_retries: number;
  llm_retry_delay: number;
  similarity_model: string;
  cutoff_threshold: number;
  duplicate_threshold: number;
  high_similarity_threshold: number;
}
