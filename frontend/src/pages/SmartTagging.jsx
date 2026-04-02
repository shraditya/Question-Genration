import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Tags,
  Sparkles,
  RefreshCw,
  Filter,
  Search,
  ChevronDown,
  CheckSquare,
  Square,
  Trash2,
  AlertCircle,
  TrendingUp
} from 'lucide-react';
import { autoTagMCQs } from '../services/api';
import toast from 'react-hot-toast';
import TagCloud from '../components/ui/TagCloud';
import ConfidenceBadge from '../components/ui/ConfidenceBadge';
import ConfidenceChart from '../components/Charts/ConfidenceChart';

export default function SmartTagging({ mcqs, setMcqs }) {
  const [loading, setLoading] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]);
  const [filterMode, setFilterMode] = useState('all'); // all, tagged, untagged, needsReview
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMCQs, setSelectedMCQs] = useState([]);
  const [showBulkActions, setShowBulkActions] = useState(false);

  // Calculate statistics
  const stats = useMemo(() => {
    const total = mcqs.length;
    const tagged = mcqs.filter(m => m.main_tag || m.tags?.length > 0).length;
    const confident = mcqs.filter(m => {
      const conf = m.confidence || 0;
      const score = conf > 1 ? conf : conf * 100;
      return score >= 80;
    }).length;
    const needsReview = mcqs.filter(m => {
      const conf = m.confidence || 0;
      const score = conf > 1 ? conf : conf * 100;
      return score < 60;
    }).length;

    return { total, tagged, confident, needsReview };
  }, [mcqs]);

  // Calculate tag distribution
  const tagDistribution = useMemo(() => {
    const tagCounts = {};
    mcqs.forEach(mcq => {
      const tags = mcq.main_tag ? [mcq.main_tag, ...(mcq.sub_tags || [])] : (mcq.tags || []);
      tags.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });

    return Object.entries(tagCounts).map(([name, count]) => ({ name, count }));
  }, [mcqs]);

  // Filter MCQs
  const filteredMCQs = useMemo(() => {
    let filtered = [...mcqs];

    // Apply tag filter
    if (selectedTags.length > 0) {
      filtered = filtered.filter(mcq => {
        const mcqTags = mcq.main_tag ? [mcq.main_tag, ...(mcq.sub_tags || [])] : (mcq.tags || []);
        return selectedTags.some(tag => mcqTags.includes(tag));
      });
    }

    // Apply mode filter
    if (filterMode === 'tagged') {
      filtered = filtered.filter(m => m.main_tag || m.tags?.length > 0);
    } else if (filterMode === 'untagged') {
      filtered = filtered.filter(m => !m.main_tag && (!m.tags || m.tags.length === 0));
    } else if (filterMode === 'needsReview') {
      filtered = filtered.filter(m => {
        const conf = m.confidence || 0;
        const score = conf > 1 ? conf : conf * 100;
        return score < 60;
      });
    }

    // Apply search
    if (searchQuery) {
      filtered = filtered.filter(m =>
        m.question.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filtered;
  }, [mcqs, selectedTags, filterMode, searchQuery]);

  const handleAutoTag = async (lowConfidenceOnly = false) => {
    setLoading(true);

    try {
      const mcqsToTag = lowConfidenceOnly
        ? mcqs.filter(m => {
            const conf = m.confidence || 0;
            const score = conf > 1 ? conf : conf * 100;
            return score < 60;
          })
        : mcqs;

      const result = await autoTagMCQs(mcqsToTag);
      setMcqs(result.mcqs);
      toast.success(
        `✅ Successfully tagged ${result.stats.tagged} MCQs!`,
        { duration: 3000 }
      );
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to auto-tag MCQs');
    } finally {
      setLoading(false);
    }
  };

  const handleTagClick = (tagName) => {
    setSelectedTags(prev =>
      prev.includes(tagName)
        ? prev.filter(t => t !== tagName)
        : [...prev, tagName]
    );
  };

  const handleSelectMCQ = (mcqIndex) => {
    setSelectedMCQs(prev =>
      prev.includes(mcqIndex)
        ? prev.filter(i => i !== mcqIndex)
        : [...prev, mcqIndex]
    );
  };

  const handleSelectAll = () => {
    if (selectedMCQs.length === filteredMCQs.length) {
      setSelectedMCQs([]);
    } else {
      setSelectedMCQs(filteredMCQs.map((_, i) => i));
    }
  };

  const handleBulkDelete = () => {
    if (window.confirm(`Delete ${selectedMCQs.length} selected questions?`)) {
      const indicesToDelete = new Set(selectedMCQs.map(i => filteredMCQs[i]));
      const newMCQs = mcqs.filter(mcq => !indicesToDelete.has(mcq));
      setMcqs(newMCQs);
      setSelectedMCQs([]);
      toast.success(`Deleted ${selectedMCQs.length} questions`);
    }
  };

  if (mcqs.length === 0) {
    return (
      <div className="card-glass text-center py-12">
        <Tags className="mx-auto text-gray-400 mb-4" size={48} />
        <h3 className="text-lg font-semibold text-gray-700">No MCQs Available</h3>
        <p className="text-gray-500 mt-2">Generate or upload MCQs to start tagging</p>
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
          <div className="bg-gradient-to-br from-emerald-500 to-green-600 p-3 rounded-2xl shadow-lg">
            <Sparkles className="text-white" size={28} />
          </div>
          <div>
            <h1 className="text-3xl font-bold gradient-text">AI-Powered Question Categorization</h1>
            <p className="text-gray-600 mt-1">Automatically tag your MCQs with hierarchical categories using advanced AI</p>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total MCQs"
          value={stats.total}
          icon={Tags}
          gradient="from-blue-500 to-cyan-500"
        />
        <StatCard
          title="Tagged MCQs"
          value={stats.tagged}
          subtitle={`${((stats.tagged / stats.total) * 100).toFixed(0)}% coverage`}
          icon={CheckSquare}
          gradient="from-emerald-500 to-green-500"
          progress={(stats.tagged / stats.total) * 100}
        />
        <StatCard
          title="High Confidence"
          value={stats.confident}
          subtitle="AI certainty >80%"
          icon={TrendingUp}
          gradient="from-green-500 to-emerald-500"
        />
        <StatCard
          title="Needs Review"
          value={stats.needsReview}
          subtitle="Confidence <60%"
          icon={AlertCircle}
          gradient="from-red-500 to-rose-500"
        />
      </div>

      {/* Tag Cloud Section */}
      <div className="card-glass">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Tags className="text-blue-600" size={24} />
          Interactive Tag Cloud
        </h2>
        <p className="text-gray-600 text-sm mb-4">
          Click tags to filter questions • Larger tags = more questions • Color-coded by category
        </p>

        {selectedTags.length > 0 && (
          <div className="mb-4 p-3 bg-blue-50 rounded-xl border border-blue-200">
            <p className="text-sm text-blue-700 font-medium">
              Filtering by: {selectedTags.join(', ')} • {filteredMCQs.length} question(s)
            </p>
          </div>
        )}

        <TagCloud
          tags={tagDistribution}
          selectedTags={selectedTags}
          onTagClick={handleTagClick}
          onTagRemove={(tag) => setSelectedTags(prev => prev.filter(t => t !== tag))}
        />
      </div>

      {/* Confidence Distribution */}
      <div className="card-glass">
        <h2 className="text-xl font-bold mb-4">AI Certainty Distribution</h2>
        <p className="text-gray-600 text-sm mb-4">
          Visual indicator of tagging quality • Tags with &lt;60% confidence need human review
        </p>
        <ConfidenceChart mcqs={mcqs} />
      </div>

      {/* Action Bar */}
      <div className="card-glass">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => handleAutoTag(false)}
              disabled={loading}
              className="btn-primary flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
                  <span>Tagging...</span>
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  <span>Auto-Tag All Questions</span>
                </>
              )}
            </button>

            <button
              onClick={() => handleAutoTag(true)}
              disabled={loading || stats.needsReview === 0}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw size={20} />
              <span>Regenerate Low Confidence</span>
              {stats.needsReview > 0 && (
                <span className="badge badge-danger">{stats.needsReview}</span>
              )}
            </button>
          </div>

          {/* Filters */}
          <div className="flex gap-3">
            <div className="relative">
              <select
                value={filterMode}
                onChange={(e) => setFilterMode(e.target.value)}
                className="input pr-10 appearance-none"
              >
                <option value="all">Show: All ({mcqs.length})</option>
                <option value="tagged">Tagged ({stats.tagged})</option>
                <option value="untagged">Untagged ({stats.total - stats.tagged})</option>
                <option value="needsReview">Needs Review ({stats.needsReview})</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" size={20} />
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="mt-4 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search questions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Bulk Actions Bar */}
      {selectedMCQs.length > 0 && (
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="fixed bottom-6 left-1/2 transform -translate-x-1/2 lg:ml-[140px] z-30"
        >
          <div className="bg-gray-900 text-white rounded-2xl shadow-2xl px-6 py-4 flex items-center gap-4">
            <span className="font-semibold">{selectedMCQs.length} selected</span>
            <div className="h-6 w-px bg-white/20"></div>
            <button
              onClick={handleBulkDelete}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500 hover:bg-red-600 transition-colors"
            >
              <Trash2 size={16} />
              <span>Delete</span>
            </button>
            <button
              onClick={() => setSelectedMCQs([])}
              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
            >
              Cancel
            </button>
          </div>
        </motion.div>
      )}

      {/* MCQ List Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">
          Questions {filteredMCQs.length > 0 && `(${filteredMCQs.length})`}
        </h2>
        {filteredMCQs.length > 0 && (
          <button
            onClick={handleSelectAll}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2"
          >
            {selectedMCQs.length === filteredMCQs.length ? (
              <CheckSquare size={16} />
            ) : (
              <Square size={16} />
            )}
            <span>Select All</span>
          </button>
        )}
      </div>

      {/* MCQ List */}
      <div className="space-y-4">
        {filteredMCQs.map((mcq, index) => (
          <MCQCard
            key={index}
            mcq={mcq}
            index={index}
            isSelected={selectedMCQs.includes(index)}
            onSelect={() => handleSelectMCQ(index)}
          />
        ))}

        {filteredMCQs.length === 0 && (
          <div className="card-glass text-center py-12">
            <Filter className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-500">No questions match your filters</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

// Stat Card Component
function StatCard({ title, value, subtitle, icon: Icon, gradient, progress }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      className={`stat-card bg-gradient-to-br ${gradient} text-white shadow-xl`}
    >
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-3">
          <p className="text-white/80 font-medium text-sm">{title}</p>
          <Icon size={24} className="text-white/80" />
        </div>
        <p className="text-4xl font-bold mb-1">{value}</p>
        {subtitle && <p className="text-white/70 text-sm">{subtitle}</p>}
        {progress !== undefined && (
          <div className="mt-3 h-2 bg-white/20 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full bg-white rounded-full"
            />
          </div>
        )}
      </div>
    </motion.div>
  );
}

// MCQ Card Component
function MCQCard({ mcq, index, isSelected, onSelect }) {
  const confidence = mcq.confidence || 0;
  const mainTag = mcq.main_tag || mcq.category;
  const subTags = mcq.sub_tags || [];
  const tags = mcq.tags || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ scale: 1.01 }}
      className={`card relative cursor-pointer ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
      onClick={onSelect}
    >
      {/* Checkbox */}
      <div className="absolute top-4 left-4">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect();
          }}
          className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
            isSelected
              ? 'bg-blue-500 border-blue-500'
              : 'border-gray-300 hover:border-blue-400'
          }`}
        >
          {isSelected && (
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>
      </div>

      <div className="pl-10">
        {/* Question */}
        <div className="flex items-start justify-between gap-4 mb-3">
          <p className="text-lg font-medium text-gray-900 flex-1">{mcq.question}</p>
          {confidence > 0 && <ConfidenceBadge confidence={confidence} size="sm" />}
        </div>

        {/* Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
          {Object.entries(mcq.options || {}).map(([key, value]) => (
            <div
              key={key}
              className={`p-3 rounded-lg border text-sm ${
                mcq.correct_answer === key
                  ? 'border-green-300 bg-green-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <span className="font-semibold text-gray-700">{key}.</span>{' '}
              <span className="text-gray-800">{value}</span>
            </div>
          ))}
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {mainTag && (
            <span className="px-3 py-1 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full text-xs font-semibold">
              {mainTag}
            </span>
          )}
          {subTags.map((tag, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium hover:bg-gray-200 transition-colors"
            >
              {tag}
            </span>
          ))}
          {!mainTag && tags.map((tag, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
