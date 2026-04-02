import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Copy, Sparkles, AlertTriangle, CheckCircle, Loader } from 'lucide-react';
import { checkSimilarity } from '../services/api';
import toast from 'react-hot-toast';
import DuplicateCluster from '../components/MCQ/DuplicateCluster';

export default function EnhancedDuplicateDetection({ mcqs, setMcqs }) {
  const [threshold, setThreshold] = useState(0.75);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [viewMode, setViewMode] = useState('cluster'); // cluster or list
  const [compareQuestion, setCompareQuestion] = useState(true);
  const [compareAnswer, setCompareAnswer] = useState(true);
  const [compareCorrectAnswer, setCompareCorrectAnswer] = useState(true);
  const [groupSimilar, setGroupSimilar] = useState(true);
  const [skippedPairs, setSkippedPairs] = useState(new Set());

  // Calculate potential duplicates count at current threshold
  const potentialCount = useMemo(() => {
    if (!results) return 0;
    return results.similar_pairs.filter(p => p.final_sim >= threshold).length;
  }, [results, threshold]);

  // Filter results by threshold and skipped pairs
  const filteredPairs = useMemo(() => {
    if (!results) return [];
    return results.similar_pairs.filter(
      p => p.final_sim >= threshold && !skippedPairs.has(`${p.idx1}-${p.idx2}`)
    );
  }, [results, threshold, skippedPairs]);

  const handleScan = async () => {
    if (mcqs.length < 2) {
      toast.error('Need at least 2 questions to check for duplicates');
      return;
    }

    setLoading(true);
    setSkippedPairs(new Set());

    try {
      const result = await checkSimilarity(mcqs, threshold);
      setResults(result);

      if (result.duplicates > 0) {
        toast.error(
          `⚠️ Found ${result.duplicates} duplicate(s) and ${result.highly_similar} highly similar pair(s)`,
          { duration: 4000 }
        );
      } else if (result.similar_pairs.length > 0) {
        toast.success(`Found ${result.similar_pairs.length} similar pair(s)`);
      } else {
        toast.success('✅ No duplicates found!');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to check similarity');
    } finally {
      setLoading(false);
    }
  };

  const handleKeep = (keepIndex) => {
    // Find and remove the other question from the pair
    const pair = filteredPairs.find(p => p.idx1 === keepIndex || p.idx2 === keepIndex);
    if (!pair) return;

    const deleteIndex = pair.idx1 === keepIndex ? pair.idx2 : pair.idx1;
    const newMCQs = mcqs.filter((_, i) => i !== deleteIndex);
    setMcqs(newMCQs);
    toast.success(`Kept question ${keepIndex + 1}, removed question ${deleteIndex + 1}`);

    // Remove this pair from results
    setSkippedPairs(prev => new Set([...prev, `${pair.idx1}-${pair.idx2}`]));
  };

  const handleDelete = (idx1, idx2) => {
    if (window.confirm('Delete both questions?')) {
      const newMCQs = mcqs.filter((_, i) => i !== idx1 && i !== idx2);
      setMcqs(newMCQs);
      toast.success(`Deleted questions ${idx1 + 1} and ${idx2 + 1}`);
      setSkippedPairs(prev => new Set([...prev, `${idx1}-${idx2}`]));
    }
  };

  const handleMerge = (pair) => {
    // For now, just keep the first one (in a real app, would show merge dialog)
    toast('Merge feature - keeping first question', { icon: '🔀' });
    handleKeep(pair.idx1);
  };

  const handleSkip = (pair) => {
    setSkippedPairs(prev => new Set([...prev, `${pair.idx1}-${pair.idx2}`]));
    toast('Pair skipped', { icon: '⏭️' });
  };

  const getThresholdLabel = (value) => {
    if (value >= 0.90) return { text: 'Very Strict', color: 'text-red-600' };
    if (value >= 0.80) return { text: 'Strict', color: 'text-orange-600' };
    if (value >= 0.70) return { text: 'Balanced', color: 'text-yellow-600' };
    return { text: 'Lenient', color: 'text-green-600' };
  };

  const thresholdLabel = getThresholdLabel(threshold);

  const stats = useMemo(() => {
    if (!results) return null;

    return {
      total: mcqs.length,
      duplicates: results.duplicates,
      unique: mcqs.length - results.duplicates,
      spaceSaved: results.duplicates > 0 ? ((results.duplicates / mcqs.length) * 100).toFixed(1) : 0
    };
  }, [results, mcqs.length]);

  if (mcqs.length < 2) {
    return (
      <div className="card-glass text-center py-12">
        <Copy className="mx-auto text-gray-400 mb-4" size={48} />
        <h3 className="text-lg font-semibold text-gray-700">Not Enough Questions</h3>
        <p className="text-gray-500 mt-2">You need at least 2 MCQs to check for duplicates</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <div className="flex items-center space-x-3 mb-2">
          <div className="bg-gradient-to-br from-orange-500 to-red-600 p-3 rounded-2xl shadow-lg">
            <Copy className="text-white" size={28} />
          </div>
          <div>
            <h1 className="text-3xl font-bold gradient-text">Smart Duplicate Detection</h1>
            <p className="text-gray-600 mt-1">Find and merge similar questions using semantic AI analysis</p>
          </div>
        </div>
      </div>

      {/* Threshold Slider */}
      <div className="card-glass">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <AlertTriangle className="text-orange-600" size={24} />
          Similarity Sensitivity
        </h2>

        <div className="space-y-4">
          {/* Slider */}
          <div className="relative">
            <input
              type="range"
              min="0.50"
              max="0.95"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full h-3 bg-gradient-to-r from-green-200 via-yellow-200 to-red-200 rounded-lg appearance-none cursor-pointer slider"
              style={{
                background: `linear-gradient(to right,
                  #86efac 0%,
                  #fde047 ${((threshold - 0.5) / 0.45) * 50}%,
                  #fca5a5 ${((threshold - 0.5) / 0.45) * 100}%)`
              }}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>0.50 (Lenient)</span>
              <span className={`font-bold ${thresholdLabel.color}`}>
                {threshold.toFixed(2)} - {thresholdLabel.text}
              </span>
              <span>0.95 (Strict)</span>
            </div>
          </div>

          {/* Live Counter */}
          {results && (
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200"
            >
              <p className="text-center">
                <span className="text-2xl font-bold text-blue-700">{potentialCount}</span>
                <span className="text-gray-600 ml-2">potential duplicate{potentialCount !== 1 ? 's' : ''} at this threshold</span>
              </p>
            </motion.div>
          )}

          {/* Threshold Indicators */}
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="p-3 rounded-lg bg-red-50 border border-red-200">
              <div className="font-semibold text-red-700">≥ 0.90 = Duplicate</div>
              <p className="text-red-600 text-xs mt-1">Almost identical questions</p>
            </div>
            <div className="p-3 rounded-lg bg-orange-50 border border-orange-200">
              <div className="font-semibold text-orange-700">0.80-0.89 = Highly Similar</div>
              <p className="text-orange-600 text-xs mt-1">Very similar, review needed</p>
            </div>
            <div className="p-3 rounded-lg bg-yellow-50 border border-yellow-200">
              <div className="font-semibold text-yellow-700">0.75-0.79 = Similar</div>
              <p className="text-yellow-600 text-xs mt-1">Some overlap, check manually</p>
            </div>
          </div>
        </div>
      </div>

      {/* Detection Settings */}
      <div className="card-glass">
        <h2 className="text-xl font-bold mb-4">Detection Settings</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors">
            <input
              type="checkbox"
              checked={compareQuestion}
              onChange={(e) => setCompareQuestion(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="font-medium text-gray-700">Compare question text</span>
          </label>

          <label className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors">
            <input
              type="checkbox"
              checked={compareAnswer}
              onChange={(e) => setCompareAnswer(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="font-medium text-gray-700">Compare answer options</span>
          </label>

          <label className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors">
            <input
              type="checkbox"
              checked={compareCorrectAnswer}
              onChange={(e) => setCompareCorrectAnswer(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="font-medium text-gray-700">Compare correct answers</span>
          </label>

          <label className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors">
            <input
              type="checkbox"
              checked={groupSimilar}
              onChange={(e) => setGroupSimilar(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="font-medium text-gray-700">Group similar questions</span>
          </label>
        </div>

        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            💡 <strong>Tip:</strong> Semantic matching finds questions with the same intent, even if worded differently
          </p>
        </div>
      </div>

      {/* Scan Button */}
      <div className="flex justify-center">
        <button
          onClick={handleScan}
          disabled={loading}
          className="btn-primary text-lg px-8 py-4"
        >
          {loading ? (
            <>
              <Loader className="animate-spin" size={24} />
              <span>Scanning for Duplicates...</span>
            </>
          ) : (
            <>
              <Copy size={24} />
              <span>🔍 Scan for Duplicates</span>
            </>
          )}
        </button>
      </div>

      {/* Statistics Panel */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card bg-gradient-to-br from-blue-500 to-cyan-500 text-white">
            <p className="text-white/80 text-sm mb-1">Total Questions</p>
            <p className="text-3xl font-bold">{stats.total}</p>
          </div>

          <div className="card bg-gradient-to-br from-red-500 to-rose-500 text-white">
            <p className="text-white/80 text-sm mb-1">Duplicates Found</p>
            <p className="text-3xl font-bold">{stats.duplicates}</p>
          </div>

          <div className="card bg-gradient-to-br from-green-500 to-emerald-500 text-white">
            <p className="text-white/80 text-sm mb-1">Unique Questions</p>
            <p className="text-3xl font-bold">{stats.unique}</p>
          </div>

          <div className="card bg-gradient-to-br from-purple-500 to-pink-500 text-white">
            <p className="text-white/80 text-sm mb-1">Space Saved</p>
            <p className="text-3xl font-bold">{stats.spaceSaved}%</p>
          </div>
        </div>
      )}

      {/* Results */}
      {results && filteredPairs.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">
              Duplicate Clusters ({filteredPairs.length})
            </h2>
          </div>

          {/* Cluster View */}
          <div className="space-y-6">
            {filteredPairs.map((pair, index) => (
              <DuplicateCluster
                key={`${pair.idx1}-${pair.idx2}`}
                pair={pair}
                mcqs={mcqs}
                onKeep={handleKeep}
                onDelete={handleDelete}
                onMerge={handleMerge}
                onSkip={handleSkip}
              />
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {results && filteredPairs.length === 0 && (
        <div className="card-glass text-center py-12 bg-green-50 border-2 border-green-200">
          <CheckCircle className="mx-auto text-green-600 mb-4" size={64} />
          <h3 className="text-2xl font-bold text-green-900 mb-2">No Duplicates Found!</h3>
          <p className="text-green-700">
            All questions are unique at the threshold of {threshold.toFixed(2)}
          </p>
        </div>
      )}
    </motion.div>
  );
}

// Add custom slider styles
const style = document.createElement('style');
style.textContent = `
  .slider::-webkit-slider-thumb {
    appearance: none;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    transition: all 0.2s;
  }

  .slider::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.6);
  }

  .slider::-moz-range-thumb {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    cursor: pointer;
    border: none;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }
`;
document.head.appendChild(style);
