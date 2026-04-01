import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Groq configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

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



# from groq import Groq

# client = Groq()
# completion = client.chat.completions.create(
#     model="llama-3.3-70b-versatile",
#     messages=[
#       {
#         "role": "user",
#         "content": "hi there"
#       }
#     ],
#     temperature=1,
#     max_completion_tokens=1024,
#     top_p=1,
#     stream=True,
#     stop=None
# )

# for chunk in completion:
#     print(chunk.choices[0].delta.content or "", end="")
