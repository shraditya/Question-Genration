import { useState } from 'react';
import { FileText, Tag, Filter, Search, Eye, EyeOff } from 'lucide-react';

export default function ViewMCQs({ mcqs, setMcqs }) {
  const [showAnswers, setShowAnswers] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTag, setFilterTag] = useState('all');

  // Get unique tags
  const allTags = new Set();
  mcqs.forEach(mcq => {
    if (mcq.main_tag) allTags.add(mcq.main_tag);
    if (mcq.tags) mcq.tags.forEach(tag => allTags.add(tag));
  });
  const uniqueTags = ['all', ...Array.from(allTags)];

  // Filter MCQs
  const filteredMcqs = mcqs.filter(mcq => {
    const matchesSearch = !searchQuery ||
      mcq.question.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesTag = filterTag === 'all' ||
      mcq.main_tag === filterTag ||
      (mcq.tags && mcq.tags.includes(filterTag));

    return matchesSearch && matchesTag;
  });

  if (mcqs.length === 0) {
    return (
      <div className="card text-center py-12">
        <FileText className="mx-auto text-gray-400 mb-4" size={48} />
        <h3 className="text-lg font-semibold text-gray-700">No MCQs Available</h3>
        <p className="text-gray-500 mt-2">
          Generate or upload MCQs to view them here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">View MCQs</h1>
        <p className="text-gray-600 mt-2">
          Review and manage your generated MCQs
        </p>
      </div>

      {/* Filters and Controls */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search questions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Filter by Tag */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <select
              value={filterTag}
              onChange={(e) => setFilterTag(e.target.value)}
              className="input pl-10 appearance-none"
            >
              {uniqueTags.map(tag => (
                <option key={tag} value={tag}>
                  {tag === 'all' ? 'All Tags' : tag}
                </option>
              ))}
            </select>
          </div>

          {/* Show Answers Toggle */}
          <button
            onClick={() => setShowAnswers(!showAnswers)}
            className="btn-secondary flex items-center justify-center space-x-2"
          >
            {showAnswers ? <EyeOff size={20} /> : <Eye size={20} />}
            <span>{showAnswers ? 'Hide' : 'Show'} Answers</span>
          </button>
        </div>

        <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
          <span>
            Showing {filteredMcqs.length} of {mcqs.length} questions
          </span>
        </div>
      </div>

      {/* MCQ List */}
      <div className="space-y-4">
        {filteredMcqs.map((mcq, index) => (
          <MCQCard
            key={index}
            mcq={mcq}
            index={index}
            showAnswers={showAnswers}
          />
        ))}
      </div>

      {filteredMcqs.length === 0 && (
        <div className="card text-center py-8">
          <p className="text-gray-500">No MCQs match your search criteria.</p>
        </div>
      )}
    </div>
  );
}

function MCQCard({ mcq, index, showAnswers }) {
  const mainTag = mcq.main_tag || mcq.category;
  const subTags = mcq.sub_tags || [];
  const difficulty = mcq.difficulty || 'medium';

  const difficultyColors = {
    easy: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    hard: 'bg-red-100 text-red-800'
  };

  return (
    <div className="card hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-bold text-primary-600">Q{index + 1}</span>
            {mainTag && (
              <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-medium">
                {mainTag}
              </span>
            )}
            <span className={`px-2 py-1 rounded text-xs font-medium ${difficultyColors[difficulty]}`}>
              {difficulty}
            </span>
          </div>
          <p className="text-lg font-medium text-gray-900">{mcq.question}</p>
        </div>
      </div>

      {/* Sub Tags */}
      {subTags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {subTags.map((tag, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Options */}
      <div className="space-y-2 mb-4">
        {Object.entries(mcq.options || {}).map(([key, value]) => (
          <div
            key={key}
            className={`p-3 rounded-lg border ${
              showAnswers && mcq.correct_answer === key
                ? 'border-green-500 bg-green-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-start space-x-2">
              <span className="font-semibold text-gray-700">{key}.</span>
              <span className="text-gray-800">{value}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Answer and Explanation */}
      {showAnswers && (
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-start space-x-2 mb-2">
            <span className="text-sm font-semibold text-green-600">Correct Answer:</span>
            <span className="text-sm text-gray-700">{mcq.correct_answer}</span>
          </div>
          {mcq.explanation && (
            <div className="mt-2">
              <span className="text-sm font-semibold text-gray-700">Explanation:</span>
              <p className="text-sm text-gray-600 mt-1">{mcq.explanation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
