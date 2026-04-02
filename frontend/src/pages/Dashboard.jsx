import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Upload, Tags, GitCompare, CheckCircle, AlertCircle, Sparkles, TrendingUp, Zap, Target } from 'lucide-react';
import { healthCheck, getConfig } from '../services/api';
import toast from 'react-hot-toast';

export default function Dashboard({ mcqs, documentLoaded }) {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const [healthData, configData] = await Promise.all([
        healthCheck(),
        getConfig()
      ]);
      setHealth(healthData);
      setConfig(configData);
    } catch (error) {
      toast.error('Failed to load system status');
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      label: 'Total MCQs',
      value: mcqs.length,
      icon: FileText,
      gradient: 'from-blue-500 to-cyan-500',
      shadowColor: 'shadow-blue-500/30',
      change: '+12%',
      changeType: 'up'
    },
    {
      label: 'Tagged MCQs',
      value: mcqs.filter(m => m.main_tag || m.tags?.length > 0).length,
      icon: Tags,
      gradient: 'from-emerald-500 to-green-500',
      shadowColor: 'shadow-emerald-500/30',
      change: '+8%',
      changeType: 'up'
    },
    {
      label: 'Document Status',
      value: documentLoaded ? 'Ready' : 'No Doc',
      icon: documentLoaded ? CheckCircle : AlertCircle,
      gradient: documentLoaded ? 'from-green-500 to-emerald-500' : 'from-gray-400 to-gray-500',
      shadowColor: documentLoaded ? 'shadow-green-500/30' : 'shadow-gray-500/20'
    }
  ];

  const quickActions = [
    {
      title: 'Upload Document',
      description: 'Upload a PDF, DOCX, or TXT file to get started',
      icon: Upload,
      action: () => navigate('/upload'),
      gradient: 'from-indigo-500 to-purple-600',
      iconBg: 'bg-indigo-100',
      iconColor: 'text-indigo-600',
      disabled: false
    },
    {
      title: 'Generate MCQs',
      description: 'Create MCQs from your uploaded document',
      icon: Sparkles,
      action: () => navigate('/generate'),
      gradient: 'from-purple-500 to-pink-600',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
      disabled: !documentLoaded
    },
    {
      title: 'Auto Tag MCQs',
      description: 'Automatically tag your MCQs with AI',
      icon: Tags,
      action: () => navigate('/tag'),
      gradient: 'from-emerald-500 to-green-600',
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
      disabled: mcqs.length === 0
    },
    {
      title: 'Check Similarity',
      description: 'Find duplicate or similar questions',
      icon: GitCompare,
      action: () => navigate('/similarity'),
      gradient: 'from-orange-500 to-red-600',
      iconBg: 'bg-orange-100',
      iconColor: 'text-orange-600',
      disabled: mcqs.length < 2
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-200px)]">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header with gradient */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-3xl p-8 shadow-2xl">
        <div className="relative z-10">
          <div className="flex items-center space-x-3 mb-2">
            <Sparkles className="text-yellow-300 animate-pulse" size={32} />
            <h1 className="text-4xl font-bold text-white">Welcome Back!</h1>
          </div>
          <p className="text-blue-100 text-lg">
            Generate, tag, and manage MCQs using RAG and AI
          </p>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24"></div>
      </div>

      {/* System Status */}
      <div className="card-glass">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold gradient-text flex items-center space-x-2">
            <Zap size={28} className="text-blue-600" />
            <span>System Status</span>
          </h2>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-green-600">All Systems Operational</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatusItem label="RAG System" status={health?.rag_system} />
          <StatusItem label="MCQ Generator" status={health?.mcq_generator} />
          <StatusItem label="Similarity Model" status={health?.similarity_model} />
        </div>

        {config && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-gray-600">Model:</span>
                <span className="font-semibold text-gray-900">{config.groq_model.split('/').pop()}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                <span className="text-gray-600">Chunk Size:</span>
                <span className="font-semibold text-gray-900">{config.chunk_size}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className="text-gray-600">Overlap:</span>
                <span className="font-semibold text-gray-900">{config.chunk_overlap}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div
              key={idx}
              className={`stat-card bg-gradient-to-br ${stat.gradient} text-white ${stat.shadowColor} shadow-xl`}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-white/80 font-medium text-sm">{stat.label}</p>
                  <Icon size={32} className="text-white/80" />
                </div>
                <div className="flex items-end justify-between">
                  <p className="text-4xl font-bold">{stat.value}</p>
                  {stat.change && (
                    <div className={`flex items-center space-x-1 px-2 py-1 rounded-lg bg-white/20 text-xs font-semibold`}>
                      <TrendingUp size={14} />
                      <span>{stat.change}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <div className="flex items-center space-x-2 mb-6">
          <Target className="text-blue-600" size={28} />
          <h2 className="text-2xl font-bold gradient-text">Quick Actions</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <button
                key={idx}
                onClick={action.action}
                disabled={action.disabled}
                className={`group card text-left transition-all duration-300 hover:shadow-2xl ${
                  action.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.03] active:scale-[0.98]'
                }`}
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="flex items-start space-x-4">
                  <div className={`${action.iconBg} p-4 rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110 ${!action.disabled && 'group-hover:rotate-6'}`}>
                    <Icon className={action.iconColor} size={28} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-lg mb-1 group-hover:gradient-text transition-all">
                      {action.title}
                    </h3>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      {action.description}
                    </p>
                    {!action.disabled && (
                      <div className="mt-3 flex items-center space-x-2 text-blue-600 font-medium text-sm group-hover:translate-x-2 transition-transform">
                        <span>Get started</span>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    )}
                    {action.disabled && (
                      <div className="mt-3 flex items-center space-x-2 text-gray-400 text-sm">
                        <AlertCircle size={14} />
                        <span>Prerequisites not met</span>
                      </div>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Getting Started Guide - if no MCQs */}
      {mcqs.length === 0 && (
        <div className="card-glass border-2 border-dashed border-blue-300">
          <div className="text-center py-8">
            <Sparkles className="mx-auto text-blue-600 mb-4 animate-pulse" size={48} />
            <h3 className="text-xl font-bold mb-2">🎯 Getting Started</h3>
            <p className="text-gray-600 mb-6">
              Start by uploading a document to generate your first MCQs!
            </p>
            <button
              onClick={() => navigate('/upload')}
              className="btn-primary"
            >
              <Upload className="inline mr-2" size={20} />
              Upload Your First Document
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusItem({ label, status }) {
  return (
    <div className={`flex items-center justify-between p-4 rounded-xl transition-all duration-300 ${
      status ? 'bg-green-50 border-2 border-green-200 hover:border-green-300' : 'bg-red-50 border-2 border-red-200'
    }`}>
      <div className="flex items-center space-x-3">
        {status ? (
          <div className="bg-green-500 p-2 rounded-lg shadow-lg">
            <CheckCircle className="text-white" size={20} />
          </div>
        ) : (
          <div className="bg-red-500 p-2 rounded-lg shadow-lg">
            <AlertCircle className="text-white" size={20} />
          </div>
        )}
        <span className={`font-semibold ${status ? 'text-green-900' : 'text-red-900'}`}>
          {label}
        </span>
      </div>
      <span className={`px-3 py-1 rounded-full text-xs font-bold ${
        status ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
      }`}>
        {status ? 'Online' : 'Offline'}
      </span>
    </div>
  );
}
