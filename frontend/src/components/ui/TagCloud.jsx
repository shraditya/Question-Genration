import { motion } from 'framer-motion';
import { X } from 'lucide-react';

const TAG_COLORS = {
  'Science': 'from-blue-500 to-cyan-500',
  'Mathematics': 'from-purple-500 to-pink-500',
  'Literature': 'from-indigo-500 to-purple-500',
  'History': 'from-amber-500 to-orange-500',
  'Geography': 'from-emerald-500 to-green-500',
  'Technology': 'from-cyan-500 to-blue-500',
  'Arts': 'from-pink-500 to-rose-500',
  'Programming': 'from-violet-500 to-purple-500',
  'default': 'from-slate-500 to-slate-600'
};

export default function TagCloud({ tags, selectedTags = [], onTagClick, onTagRemove }) {
  const getTagColor = (tag) => {
    // Check if tag matches any category
    for (const [category, color] of Object.entries(TAG_COLORS)) {
      if (tag.toLowerCase().includes(category.toLowerCase()) || category.toLowerCase().includes(tag.toLowerCase())) {
        return color;
      }
    }
    return TAG_COLORS.default;
  };

  // Sort tags by count (descending)
  const sortedTags = [...tags].sort((a, b) => b.count - a.count);

  // Calculate font sizes based on count
  const maxCount = Math.max(...tags.map(t => t.count));
  const minCount = Math.min(...tags.map(t => t.count));
  const getFontSize = (count) => {
    if (maxCount === minCount) return 'text-base';
    const ratio = (count - minCount) / (maxCount - minCount);
    if (ratio > 0.7) return 'text-xl';
    if (ratio > 0.4) return 'text-lg';
    return 'text-base';
  };

  return (
    <div className="flex flex-wrap gap-3">
      {sortedTags.map((tag, index) => {
        const isSelected = selectedTags.includes(tag.name);
        const gradient = getTagColor(tag.name);

        return (
          <motion.button
            key={tag.name}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ scale: 1.1, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onTagClick(tag.name)}
            className={`
              group relative inline-flex items-center gap-2 px-4 py-2 rounded-full
              font-semibold transition-all duration-300 cursor-pointer
              ${getFontSize(tag.count)}
              ${isSelected
                ? `bg-gradient-to-r ${gradient} text-white shadow-lg`
                : 'bg-white text-gray-700 hover:shadow-md border-2 border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <span>{tag.name}</span>
            <span className={`
              px-2 py-0.5 rounded-full text-xs font-bold
              ${isSelected ? 'bg-white/20' : 'bg-gray-100 text-gray-600'}
            `}>
              {tag.count}
            </span>

            {isSelected && onTagRemove && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onTagRemove(tag.name);
                }}
                className="p-0.5 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
              >
                <X size={14} />
              </button>
            )}

            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
              {tag.count} question{tag.count !== 1 ? 's' : ''} • Click to filter
            </div>
          </motion.button>
        );
      })}

      {tags.length === 0 && (
        <div className="text-gray-400 text-sm italic">
          No tags yet. Auto-tag your MCQs to see them here.
        </div>
      )}
    </div>
  );
}
