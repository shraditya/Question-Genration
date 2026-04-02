import { useState } from 'react';
import { Tags, Sparkles, AlertCircle, TrendingUp } from 'lucide-react';
import { autoTagMCQs } from '../services/api';
import toast from 'react-hot-toast';

export default function AutoTag({ mcqs, setMcqs }) {
  const [tagging, setTagging] = useState(false);
  const [tagStats, setTagStats] = useState(null);

  const handleAutoTag = async () => {
    setTagging(true);

    try {
      const result = await autoTagMCQs(mcqs);
      toast.success(result.message);
      setMcqs(result.mcqs);
      setTagStats(result.stats);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to tag MCQs');
    } finally {
      setTagging(false);
    }
  };

  // Calculate current stats
  const currentTagged = mcqs.filter(m => m.main_tag || m.tags?.length > 0).length;
  const currentConfident = mcqs.filter(m => m.confident).length;

  if (mcqs.length === 0) {
    return (
      <div className="card">
        <div className="flex items-start space-x-3 text-amber-600">
          <AlertCircle size={24} className="flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-lg">No MCQs Available</h3>
            <p className="text-gray-600 mt-2">
              Please generate or upload MCQs before auto-tagging.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Auto Tag MCQs</h1>
        <p className="text-gray-600 mt-2">
          Automatically tag your MCQs with hierarchical main tags and sub-tags using AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Stats */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Current Statistics</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-600">Total MCQs</p>
                <p className="text-2xl font-bold">{mcqs.length}</p>
              </div>
              <Tags className="text-gray-400" size={32} />
            </div>

            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <p className="text-sm text-blue-600">Tagged MCQs</p>
                <p className="text-2xl font-bold text-blue-700">{currentTagged}</p>
                <p className="text-xs text-blue-600 mt-1">
                  {((currentTagged / mcqs.length) * 100).toFixed(1)}%
                </p>
              </div>
              <TrendingUp className="text-blue-400" size={32} />
            </div>

            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div>
                <p className="text-sm text-green-600">Confident Tags</p>
                <p className="text-2xl font-bold text-green-700">{currentConfident}</p>
                <p className="text-xs text-green-600 mt-1">
                  {((currentConfident / mcqs.length) * 100).toFixed(1)}%
                </p>
              </div>
              <Sparkles className="text-green-400" size={32} />
            </div>
          </div>

          <button
            onClick={handleAutoTag}
            disabled={tagging}
            className="btn-primary w-full mt-6 flex items-center justify-center space-x-2"
          >
            {tagging ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Tagging...</span>
              </>
            ) : (
              <>
                <Tags size={20} />
                <span>Auto Tag All MCQs</span>
              </>
            )}
          </button>
        </div>

        {/* Information */}
        <div className="card bg-purple-50 border border-purple-200">
          <h2 className="text-xl font-semibold mb-4 text-purple-900">How Auto-Tagging Works</h2>

          <div className="space-y-3 text-sm text-purple-800">
            <div className="flex items-start space-x-2">
              <div className="bg-purple-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">1</span>
              </div>
              <p>
                The system uses Groq LLM to analyze each question and generate
                relevant tags
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-purple-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">2</span>
              </div>
              <p>
                Each MCQ receives a <strong>main tag</strong> (primary category) and
                up to 3 <strong>sub-tags</strong> (specific topics)
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-purple-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">3</span>
              </div>
              <p>
                Tags are hierarchical: main tag provides broad categorization,
                sub-tags add granular detail
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-purple-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">4</span>
              </div>
              <p>
                Confidence scores indicate how certain the AI is about the tags
              </p>
            </div>

            <div className="mt-4 p-3 bg-purple-100 rounded-lg">
              <p className="text-xs">
                <strong>Example:</strong> A Python programming question might get
                <span className="font-mono bg-white px-1 rounded mx-1">main_tag: "Programming"</span>
                and
                <span className="font-mono bg-white px-1 rounded mx-1">sub_tags: ["Python", "Functions", "Data Types"]</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tagging Progress */}
      {tagging && (
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <div>
              <p className="font-medium">Tagging {mcqs.length} MCQs...</p>
              <p className="text-sm text-gray-600">
                This may take a moment. The LLM is analyzing each question.
              </p>
            </div>
          </div>

          <div className="mt-4 bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="bg-primary-600 h-full animate-pulse" style={{ width: '100%' }}></div>
          </div>
        </div>
      )}

      {/* Results */}
      {tagStats && !tagging && (
        <div className="card bg-green-50 border border-green-200">
          <h2 className="text-xl font-semibold mb-4 text-green-900">Tagging Complete!</h2>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-green-600">Total</p>
              <p className="text-2xl font-bold text-green-700">{tagStats.total}</p>
            </div>
            <div>
              <p className="text-sm text-green-600">Tagged</p>
              <p className="text-2xl font-bold text-green-700">{tagStats.tagged}</p>
            </div>
            <div>
              <p className="text-sm text-green-600">Confident</p>
              <p className="text-2xl font-bold text-green-700">{tagStats.confident}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tagged MCQs Preview */}
      {mcqs.filter(m => m.main_tag).length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Tagged MCQs Preview</h2>

          <div className="space-y-3">
            {mcqs.slice(0, 5).map((mcq, idx) => (
              <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-900 mb-2 line-clamp-1">
                  {mcq.question}
                </p>
                <div className="flex flex-wrap gap-2">
                  {mcq.main_tag && (
                    <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-medium">
                      {mcq.main_tag}
                    </span>
                  )}
                  {mcq.sub_tags?.map((tag, i) => (
                    <span key={i} className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
