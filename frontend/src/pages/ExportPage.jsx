import { useState } from 'react';
import { Download, FileJson, FileText, AlertCircle } from 'lucide-react';
import { exportMCQs } from '../services/api';
import toast from 'react-hot-toast';

export default function ExportPage({ mcqs }) {
  const [format, setFormat] = useState('json');
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    setExporting(true);

    try {
      await exportMCQs(mcqs, format);
      toast.success(`MCQs exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to export MCQs');
    } finally {
      setExporting(false);
    }
  };

  if (mcqs.length === 0) {
    return (
      <div className="card">
        <div className="flex items-start space-x-3 text-amber-600">
          <AlertCircle size={24} className="flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-lg">No MCQs Available</h3>
            <p className="text-gray-600 mt-2">
              Please generate or upload MCQs before exporting.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Export MCQs</h1>
        <p className="text-gray-600 mt-2">
          Download your MCQs in JSON or CSV format
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Export Options */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Export Options</h2>

          <div className="space-y-4">
            {/* Format Selection */}
            <div>
              <label className="label">Select Format</label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setFormat('json')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    format === 'json'
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <FileJson className={`mx-auto mb-2 ${format === 'json' ? 'text-primary-600' : 'text-gray-400'}`} size={32} />
                  <p className="font-medium">JSON</p>
                  <p className="text-xs text-gray-500 mt-1">Structured data</p>
                </button>

                <button
                  onClick={() => setFormat('csv')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    format === 'csv'
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <FileText className={`mx-auto mb-2 ${format === 'csv' ? 'text-primary-600' : 'text-gray-400'}`} size={32} />
                  <p className="font-medium">CSV</p>
                  <p className="text-xs text-gray-500 mt-1">Spreadsheet</p>
                </button>
              </div>
            </div>

            {/* Export Stats */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium mb-2">Export Summary</h3>
              <div className="space-y-1 text-sm text-gray-600">
                <p>Total MCQs: <span className="font-medium text-gray-900">{mcqs.length}</span></p>
                <p>
                  Tagged: <span className="font-medium text-gray-900">
                    {mcqs.filter(m => m.main_tag || m.tags?.length > 0).length}
                  </span>
                </p>
                <p>Format: <span className="font-medium text-gray-900">{format.toUpperCase()}</span></p>
              </div>
            </div>

            {/* Export Button */}
            <button
              onClick={handleExport}
              disabled={exporting}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {exporting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Exporting...</span>
                </>
              ) : (
                <>
                  <Download size={20} />
                  <span>Export as {format.toUpperCase()}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Format Information */}
        <div className="space-y-6">
          {/* JSON Info */}
          <div className={`card ${format === 'json' ? 'border-2 border-primary-500' : ''}`}>
            <div className="flex items-start space-x-3">
              <FileJson className="text-primary-600 flex-shrink-0" size={24} />
              <div>
                <h3 className="font-semibold text-lg mb-2">JSON Format</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Best for programmatic access and data processing
                </p>
                <div className="bg-gray-900 text-green-400 p-3 rounded text-xs font-mono overflow-x-auto">
                  {`{
  "mcqs": [
    {
      "question": "...",
      "options": {
        "A": "...",
        "B": "..."
      },
      "correct_answer": "A",
      "explanation": "...",
      "main_tag": "...",
      "sub_tags": ["..."]
    }
  ]
}`}
                </div>
              </div>
            </div>
          </div>

          {/* CSV Info */}
          <div className={`card ${format === 'csv' ? 'border-2 border-primary-500' : ''}`}>
            <div className="flex items-start space-x-3">
              <FileText className="text-primary-600 flex-shrink-0" size={24} />
              <div>
                <h3 className="font-semibold text-lg mb-2">CSV Format</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Best for Excel, Google Sheets, and data analysis
                </p>
                <div className="bg-gray-900 text-green-400 p-3 rounded text-xs font-mono overflow-x-auto whitespace-pre">
                  {`Question,Option A,Option B,...
"What is...","Answer 1","Answer 2",...`}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Includes: Question, Options A-D, Correct Answer, Explanation, Main Tag, Sub Tags
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">MCQs Preview (First 3)</h2>
        <div className="space-y-3">
          {mcqs.slice(0, 3).map((mcq, idx) => (
            <div key={idx} className="p-4 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900 mb-2">{idx + 1}. {mcq.question}</p>
              <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                {Object.entries(mcq.options || {}).map(([key, value]) => (
                  <div key={key} className={mcq.correct_answer === key ? 'text-green-600 font-medium' : ''}>
                    {key}. {value}
                  </div>
                ))}
              </div>
              {mcq.main_tag && (
                <div className="mt-2 flex flex-wrap gap-2">
                  <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs">
                    {mcq.main_tag}
                  </span>
                  {mcq.sub_tags?.map((tag, i) => (
                    <span key={i} className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
