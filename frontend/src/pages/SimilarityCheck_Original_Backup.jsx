import { useState } from 'react';
import { GitCompare, AlertCircle, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { checkSimilarity } from '../services/api';
import toast from 'react-hot-toast';

export default function SimilarityCheck({ mcqs }) {
  const [threshold, setThreshold] = useState(0.75);
  const [checking, setChecking] = useState(false);
  const [results, setResults] = useState(null);

  const handleCheck = async () => {
    setChecking(true);

    try {
      const result = await checkSimilarity(mcqs, threshold);
      setResults(result);

      if (result.duplicates > 0) {
        toast.error(`Found ${result.duplicates} duplicate(s)!`);
      } else if (result.similar_pairs.length > 0) {
        toast.success(`Found ${result.similar_pairs.length} similar pair(s)`);
      } else {
        toast.success('No similar questions found');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to check similarity');
    } finally {
      setChecking(false);
    }
  };

  if (mcqs.length < 2) {
    return (
      <div className="card">
        <div className="flex items-start space-x-3 text-amber-600">
          <AlertCircle size={24} className="flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-lg">Not Enough MCQs</h3>
            <p className="text-gray-600 mt-2">
              You need at least 2 MCQs to check for similarity.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const chartData = results
    ? [
        { name: 'Duplicates', count: results.duplicates, fill: '#ef4444' },
        { name: 'Highly Similar', count: results.highly_similar, fill: '#f59e0b' },
        { name: 'Similar', count: results.similar, fill: '#3b82f6' }
      ]
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Similarity Check</h1>
        <p className="text-gray-600 mt-2">
          Find duplicate and similar MCQs using fine-tuned AI model
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Configuration</h2>

          <div className="space-y-4">
            <div>
              <label className="label">
                Similarity Threshold: {threshold.toFixed(2)}
              </label>
              <input
                type="range"
                min="0.50"
                max="0.95"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full"
                disabled={checking}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0.50 (Lenient)</span>
                <span>0.95 (Strict)</span>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-start space-x-2">
                <Info className="text-blue-600 flex-shrink-0 mt-0.5" size={16} />
                <div className="text-xs text-blue-800">
                  <p className="font-medium mb-1">Thresholds:</p>
                  <p>• Duplicate: ≥ 0.90</p>
                  <p>• Highly Similar: ≥ 0.80</p>
                  <p>• Similar: ≥ {threshold.toFixed(2)}</p>
                </div>
              </div>
            </div>

            <button
              onClick={handleCheck}
              disabled={checking}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {checking ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Checking...</span>
                </>
              ) : (
                <>
                  <GitCompare size={20} />
                  <span>Check Similarity</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* How it Works */}
        <div className="card bg-indigo-50 border border-indigo-200">
          <h2 className="text-xl font-semibold mb-4 text-indigo-900">How it Works</h2>

          <div className="space-y-3 text-sm text-indigo-800">
            <div className="flex items-start space-x-2">
              <div className="bg-indigo-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">1</span>
              </div>
              <p>
                Uses a fine-tuned sentence-transformer model trained specifically
                for MCQ intent similarity
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-indigo-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">2</span>
              </div>
              <p>
                Compares both questions AND answers using adaptive weighting
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-indigo-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">3</span>
              </div>
              <p>
                Answer weight = 0.15 + 0.70 × (1 − question_sim)
              </p>
            </div>

            <div className="flex items-start space-x-2">
              <div className="bg-indigo-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold">4</span>
              </div>
              <p>
                Reports shared tags between similar questions for better context
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      {results && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card bg-red-50 border border-red-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-red-600">Duplicates</p>
                  <p className="text-3xl font-bold text-red-700">{results.duplicates}</p>
                </div>
                <AlertCircle className="text-red-400" size={32} />
              </div>
            </div>

            <div className="card bg-amber-50 border border-amber-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-amber-600">Highly Similar</p>
                  <p className="text-3xl font-bold text-amber-700">{results.highly_similar}</p>
                </div>
                <AlertTriangle className="text-amber-400" size={32} />
              </div>
            </div>

            <div className="card bg-blue-50 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600">Similar</p>
                  <p className="text-3xl font-bold text-blue-700">{results.similar}</p>
                </div>
                <CheckCircle className="text-blue-400" size={32} />
              </div>
            </div>
          </div>

          {/* Chart */}
          {chartData.some(d => d.count > 0) && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Similarity Distribution</h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Similar Pairs */}
          {results.similar_pairs.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">
                Similar Pairs ({results.similar_pairs.length})
              </h2>

              <div className="space-y-4">
                {results.similar_pairs.slice(0, 10).map((pair, idx) => (
                  <SimilarPairCard key={idx} pair={pair} />
                ))}
              </div>

              {results.similar_pairs.length > 10 && (
                <p className="text-sm text-gray-500 mt-4 text-center">
                  Showing 10 of {results.similar_pairs.length} similar pairs
                </p>
              )}
            </div>
          )}

          {results.similar_pairs.length === 0 && (
            <div className="card bg-green-50 border border-green-200 text-center py-8">
              <CheckCircle className="mx-auto text-green-600 mb-3" size={48} />
              <h3 className="text-lg font-semibold text-green-900">No Similar Questions Found!</h3>
              <p className="text-green-700 mt-2">
                All questions are unique at the threshold of {threshold.toFixed(2)}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function SimilarPairCard({ pair }) {
  const getLabelColor = (label) => {
    switch (label) {
      case 'Duplicate':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'Highly Similar':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'Similar':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex items-start justify-between mb-3">
        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getLabelColor(pair.label)}`}>
          {pair.label}
        </span>
        <div className="text-right">
          <p className="text-sm text-gray-600">Similarity Score</p>
          <p className="text-lg font-bold text-gray-900">{(pair.final_sim * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="p-3 bg-white rounded border border-gray-200">
          <p className="text-xs text-gray-500 mb-1">Question {pair.idx1 + 1}</p>
          <p className="text-sm text-gray-900">{pair.q1}</p>
        </div>

        <div className="p-3 bg-white rounded border border-gray-200">
          <p className="text-xs text-gray-500 mb-1">Question {pair.idx2 + 1}</p>
          <p className="text-sm text-gray-900">{pair.q2}</p>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-gray-600">
        <div className="flex space-x-4">
          <span>Q: {(pair.question_sim * 100).toFixed(1)}%</span>
          <span>A: {(pair.answer_sim * 100).toFixed(1)}%</span>
          <span>Weight: {(pair.answer_weight * 100).toFixed(1)}%</span>
        </div>
        {pair.shared_tags.length > 0 && (
          <div className="flex items-center space-x-1">
            <span>Tags:</span>
            {pair.shared_tags.map((tag, i) => (
              <span key={i} className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
