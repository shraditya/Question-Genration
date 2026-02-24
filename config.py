import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Groq configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')

    # ChromaDB configuration
    CHROMA_PERSIST_DIR = "./chroma_db"

    # MCQ generation settings
    MAX_QUESTIONS = 30
    MIN_QUESTIONS = 1

    # Text processing settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1200))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

    # LLM settings
    LLM_RETRIES = int(os.getenv('LLM_RETRIES', 3))
    LLM_RETRY_DELAY = float(os.getenv('LLM_RETRY_DELAY', 1.5))
