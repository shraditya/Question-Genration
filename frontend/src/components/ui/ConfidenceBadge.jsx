import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';

export default function ConfidenceBadge({ confidence, showLabel = true, size = 'md' }) {
  // Convert confidence to 0-100 scale if it's 0-1
  const score = confidence > 1 ? confidence : confidence * 100;

  const getConfidenceLevel = (score) => {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
  };

  const level = getConfidenceLevel(score);

  const config = {
    high: {
      color: 'from-emerald-500 to-green-500',
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      icon: CheckCircle,
      label: 'High Confidence',
      description: 'AI is certain about this tag'
    },
    medium: {
      color: 'from-amber-500 to-orange-500',
      bg: 'bg-amber-50',
      text: 'text-amber-700',
      icon: AlertTriangle,
      label: 'Medium Confidence',
      description: 'Tag may need review'
    },
    low: {
      color: 'from-red-500 to-rose-500',
      bg: 'bg-red-50',
      text: 'text-red-700',
      icon: AlertCircle,
      label: 'Low Confidence',
      description: 'Human review recommended'
    }
  };

  const { color, bg, text, icon: Icon, label, description } = config[level];

  const sizes = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="group relative inline-block"
    >
      <div className={`
        inline-flex items-center gap-2 rounded-full font-semibold
        bg-gradient-to-r ${color} text-white shadow-md
        ${sizes[size]}
      `}>
        <Icon size={size === 'sm' ? 12 : size === 'lg' ? 18 : 14} />
        <span>{Math.round(score)}%</span>
        {showLabel && size !== 'sm' && (
          <span className="hidden sm:inline text-white/90 font-medium">
            {level === 'high' ? 'Confident' : level === 'medium' ? 'Moderate' : 'Review'}
          </span>
        )}
      </div>

      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10 shadow-xl">
        <div className="font-semibold mb-1">{label}</div>
        <div className="text-gray-300">{description}</div>
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
          <div className="border-4 border-transparent border-t-gray-900"></div>
        </div>
      </div>
    </motion.div>
  );
}
