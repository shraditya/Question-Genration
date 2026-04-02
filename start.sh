#!/bin/bash

# RAG MCQ Generator - Startup Script
# This script starts both backend and frontend

echo "🚀 Starting RAG MCQ Generator..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Activate conda environment
echo -e "${BLUE}🐍 Activating conda environment: rag_mcq${NC}"
eval "$(conda shell.bash hook)"
conda activate rag_mcq

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to activate conda environment 'rag_mcq'${NC}"
    echo "Please create it first or activate manually:"
    echo "  conda activate rag_mcq"
    exit 1
fi

echo -e "${GREEN}✅ Conda environment activated${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file with GROQ_API_KEY"
    echo ""
    echo "Example:"
    echo "GROQ_API_KEY=your_key_here"
    echo "MODEL_PATH=/Users/k/rag_questions/similiarty /mcq_intent_model"
    exit 1
fi

# Check if similarity model exists
MODEL_PATH=$(grep MODEL_PATH .env | cut -d '=' -f2)
if [ -n "$MODEL_PATH" ] && [ ! -d "$MODEL_PATH" ]; then
    echo -e "${YELLOW}⚠️  Warning: Similarity model not found at: $MODEL_PATH${NC}"
    echo "Similarity checking may not work."
    echo ""
fi

# Check if node_modules exists in frontend
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo ""
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend
echo -e "${GREEN}🔧 Starting Backend (FastAPI)...${NC}"
python run_backend.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}⚛️  Starting Frontend (React)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ Both servers started!${NC}"
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
