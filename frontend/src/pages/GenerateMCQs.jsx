import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Sparkles, AlertCircle } from 'lucide-react';
import { generateMCQs } from '../services/api';
import toast from 'react-hot-toast';

export default function GenerateMCQs({ documentLoaded, setMcqs }) {
  const navigate = useNavigate();
  const [numQuestions, setNumQuestions] = useState(10);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);

    try {
      const result = await generateMCQs(numQuestions);
      toast.success(result.message);
      setMcqs(result.mcqs);

      // Navigate to view page
      setTimeout(() => {
        navigate('/mcqs');
      }, 1000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate MCQs');
    } finally {
      setGenerating(false);
    }
  };

  if (!documentLoaded) {
    return (
      <div className="card">
        <div className="flex items-start space-x-3 text-amber-600">
          <AlertCircle size={24} className="flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-lg">No Document Loaded</h3>
            <p className="text-gray-600 mt-2">
              Please upload a document first before generating MCQs.
            </p>
            <button
              onClick={() => navigate('/upload')}
              className="btn-primary mt-4"
            >
              Go to Upload
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Generate MCQs</h1>
        <p className="text-gray-600 mt-2">
          Generate multiple-choice questions from your uploaded document using AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Configuration</h2>

          <div className="space-y-4">
            <div>
              <label className="label">Number of Questions</label>
              <input
                type="number"
                min="1"
                max="30"
                value={numQuestions}
                onChange={(e) => setNumQuestions(parseInt(e.target.value) || 1)}
                className="input"
                disabled={generating}
              />
              <p className="text-xs text-gray-500 mt-1">
                Range: 1-30 questions
              </p>
            </div>

            <div className="pt-4">
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={20} />
                    <span>Generate MCQs</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Information */}
        <div className="card bg-blue-50 border border-blue-200">
          <h2 className="text-xl font-semibold mb-4 text-blue-900">How it works</h2>

          <div className="space-y-3 text-sm text-blue-800">
            <div className="flex items-start space-x-2">
              <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">1</span>
              </div>
              <p>
                The system uses RAG (Retrieval-Augmented Generation) to find relevant
                chunks from your document
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">2</span>
              </div>
              <p>
                An AI language model generates high-quality MCQs based on the
                retrieved context
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">3</span>
              </div>
              <p>
                Each MCQ includes a question, 4 options, correct answer, and
                explanation
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">4</span>
              </div>
              <p>
                You can refine, tag, and check for duplicates after generation
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Generation Progress */}
      {generating && (
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <div>
              <p className="font-medium">Generating {numQuestions} MCQs...</p>
              <p className="text-sm text-gray-600">
                This may take a moment. Please wait.
              </p>
            </div>
          </div>

          <div className="mt-4 bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="bg-primary-600 h-full animate-pulse" style={{ width: '100%' }}></div>
          </div>
        </div>
      )}
    </div>
  );
}
