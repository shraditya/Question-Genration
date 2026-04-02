#!/usr/bin/env python3
"""
Run backend server from project root
This ensures proper import paths

NOTE: Run this with the rag_mcq conda environment:
  conda activate rag_mcq
  python run_backend.py
"""

import os
import sys

# Change to script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(f"📁 Working directory: {os.getcwd()}")
print(f"🐍 Python: {sys.executable}")

# Add to path
sys.path.insert(0, script_dir)

# Import and run
try:
    print("🚀 Starting FastAPI server...")
    import uvicorn
    from backend.api import app

    port = int(os.getenv('PORT', 8000))

    print(f"\n{'='*60}")
    print(f"🚀 RAG MCQ Generator API")
    print(f"{'='*60}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"{'='*60}\n")

    # Run without reload to avoid import string warning
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
