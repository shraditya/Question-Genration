import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { FileText, Upload, Tags, GitCompare, Download, Home, Sparkles, Menu, X } from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import DocumentUpload from './pages/DocumentUpload';
import GenerateMCQs from './pages/GenerateMCQs';
import ViewMCQs from './pages/ViewMCQs';
import AutoTag from './pages/AutoTag';
import SimilarityCheck from './pages/SimilarityCheck';
import ExportPage from './pages/ExportPage';

function Navigation() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home, color: 'blue' },
    { path: '/upload', label: 'Upload', icon: Upload, color: 'indigo' },
    { path: '/generate', label: 'Generate', icon: Sparkles, color: 'purple' },
    { path: '/mcqs', label: 'View MCQs', icon: FileText, color: 'cyan' },
    { path: '/tag', label: 'Auto Tag', icon: Tags, color: 'emerald' },
    { path: '/similarity', label: 'Similarity', icon: GitCompare, color: 'orange' },
    { path: '/export', label: 'Export', icon: Download, color: 'pink' },
  ];

  return (
    <nav className="bg-white/80 backdrop-blur-2xl shadow-lg border-b border-white/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-xl shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
              <Sparkles className="text-white" size={28} />
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">RAG MCQ Generator</h1>
              <p className="text-xs text-gray-500">Powered by AI</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`group relative flex items-center space-x-2 px-5 py-2.5 rounded-xl transition-all duration-300 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30'
                      : 'text-gray-600 hover:bg-gray-100 hover:scale-105'
                  }`}
                >
                  <Icon size={18} className={isActive ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'} />
                  <span className="text-sm font-semibold">{item.label}</span>
                  {isActive && (
                    <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1/2 h-1 bg-white rounded-full"></div>
                  )}
                </Link>
              );
            })}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl hover:bg-gray-100 transition-colors"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden pb-4 animate-slide-in-top">
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

function App() {
  const [mcqs, setMcqs] = useState([]);
  const [documentLoaded, setDocumentLoaded] = useState(false);

  return (
    <Router>
      <div className="min-h-screen">
        <Navigation />

        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard mcqs={mcqs} documentLoaded={documentLoaded} />} />
            <Route
              path="/upload"
              element={<DocumentUpload setDocumentLoaded={setDocumentLoaded} setMcqs={setMcqs} />}
            />
            <Route
              path="/generate"
              element={<GenerateMCQs documentLoaded={documentLoaded} setMcqs={setMcqs} />}
            />
            <Route path="/mcqs" element={<ViewMCQs mcqs={mcqs} setMcqs={setMcqs} />} />
            <Route path="/tag" element={<AutoTag mcqs={mcqs} setMcqs={setMcqs} />} />
            <Route path="/similarity" element={<SimilarityCheck mcqs={mcqs} />} />
            <Route path="/export" element={<ExportPage mcqs={mcqs} />} />
          </Routes>
        </main>

        {/* Floating gradient orbs for visual appeal */}
        <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden -z-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float"></div>
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: '1s' }}></div>
          <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-indigo-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: '2s' }}></div>
        </div>

        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#fff',
              color: '#363636',
              padding: '16px',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
