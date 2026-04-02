import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence } from 'framer-motion';

// Layout
import MainLayout from './components/Layout/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import DocumentUpload from './pages/DocumentUpload';
import GenerateMCQs from './pages/GenerateMCQs';
import ViewMCQs from './pages/ViewMCQs';
import AutoTag from './pages/AutoTag';
import SimilarityCheck from './pages/SimilarityCheck';
import ExportPage from './pages/ExportPage';

function App() {
  const [mcqs, setMcqs] = useState([]);
  const [documentLoaded, setDocumentLoaded] = useState(false);

  return (
    <Router>
      <MainLayout>
        <AnimatePresence mode="wait">
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
        </AnimatePresence>

        {/* Floating gradient orbs removed - cleaner with sidebar */}

        <Toaster
          position="top-right"
          toastOptions={{
            className: 'lg:ml-[280px]', // Offset for sidebar
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
      </MainLayout>
    </Router>
  );
}

export default App;
