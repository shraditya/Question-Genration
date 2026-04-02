import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, File, X, CheckCircle, Cloud, Sparkles } from 'lucide-react';
import { uploadFile, uploadText, uploadMCQFile } from '../services/api';
import toast from 'react-hot-toast';

export default function DocumentUpload({ setDocumentLoaded, setMcqs }) {
  const [activeTab, setActiveTab] = useState('file'); // file, text, mcq
  const [text, setText] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // File dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleFileUpload(acceptedFiles[0]);
      }
    }
  });

  // MCQ file dropzone
  const mcqDropzone = useDropzone({
    accept: {
      'application/json': ['.json'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleMCQFileUpload(acceptedFiles[0]);
      }
    }
  });

  const handleFileUpload = async (file) => {
    setUploading(true);
    setUploadedFile(file);
    setUploadProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 90));
    }, 200);

    try {
      const result = await uploadFile(file);
      setUploadProgress(100);
      toast.success(result.message);
      setDocumentLoaded(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload file');
      setUploadedFile(null);
      setUploadProgress(0);
    } finally {
      clearInterval(progressInterval);
      setUploading(false);
    }
  };

  const handleTextUpload = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 15, 90));
    }, 100);

    try {
      const result = await uploadText(text);
      setUploadProgress(100);
      toast.success(result.message);
      setDocumentLoaded(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload text');
      setUploadProgress(0);
    } finally {
      clearInterval(progressInterval);
      setUploading(false);
    }
  };

  const handleMCQFileUpload = async (file) => {
    setUploading(true);
    setUploadProgress(0);

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 90));
    }, 150);

    try {
      const result = await uploadMCQFile(file);
      setUploadProgress(100);
      toast.success(result.message);
      setMcqs(result.mcqs);
      setUploadedFile(file);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload MCQ file');
      setUploadProgress(0);
    } finally {
      clearInterval(progressInterval);
      setUploading(false);
    }
  };

  const clearFile = () => {
    setUploadedFile(null);
    setUploadProgress(0);
  };

  const tabs = [
    { id: 'file', label: 'Upload Document', icon: Upload },
    { id: 'text', label: 'Paste Text', icon: FileText },
    { id: 'mcq', label: 'Load MCQ File', icon: File }
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-3xl p-8 shadow-2xl">
        <div className="relative z-10">
          <div className="flex items-center space-x-3 mb-2">
            <Cloud className="text-white animate-pulse" size={32} />
            <h1 className="text-4xl font-bold text-white">Upload Document</h1>
          </div>
          <p className="text-indigo-100 text-lg">
            Upload a document to generate MCQs or load existing MCQ files
          </p>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
      </div>

      {/* Tabs */}
      <div className="card-glass">
        <div className="flex flex-wrap gap-2 mb-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/30 scale-105'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:scale-105'
                }`}
              >
                <Icon size={20} className={activeTab === tab.id ? 'animate-pulse' : ''} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* File Upload Tab */}
        {activeTab === 'file' && (
          <div className="space-y-4">
            {!uploadedFile ? (
              <div
                {...getRootProps()}
                className={`relative border-4 border-dashed rounded-3xl p-16 text-center cursor-pointer transition-all duration-300 ${
                  isDragActive
                    ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 scale-[1.02] shadow-xl'
                    : 'border-gray-300 hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-50/50 hover:to-indigo-50/50 hover:scale-[1.01]'
                }`}
              >
                <input {...getInputProps()} />
                <div className={`transition-all duration-300 ${isDragActive ? 'scale-110' : ''}`}>
                  <Upload
                    className={`mx-auto mb-6 ${isDragActive ? 'text-blue-600 animate-bounce' : 'text-gray-400'}`}
                    size={64}
                  />
                  <p className="text-xl font-bold text-gray-700 mb-3">
                    {isDragActive ? '✨ Drop it here!' : '📁 Drag & drop your file here'}
                  </p>
                  <p className="text-gray-500 mb-4">or click to browse from your computer</p>
                  <div className="flex items-center justify-center space-x-4 text-sm text-gray-400">
                    <span className="badge bg-blue-100 text-blue-600">PDF</span>
                    <span className="badge bg-indigo-100 text-indigo-600">DOCX</span>
                    <span className="badge bg-purple-100 text-purple-600">TXT</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="relative overflow-hidden bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-6 shadow-lg animate-slide-in-bottom">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-4 rounded-2xl shadow-lg">
                      <File className="text-white" size={32} />
                    </div>
                    <div>
                      <p className="font-bold text-lg text-gray-900">{uploadedFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {(uploadedFile.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={clearFile}
                    className="p-2 rounded-xl hover:bg-red-100 text-red-500 hover:text-red-700 transition-all hover:scale-110"
                  >
                    <X size={24} />
                  </button>
                </div>
              </div>
            )}

            {uploading && (
              <div className="space-y-3 animate-slide-in-bottom">
                <div className="flex items-center justify-between text-sm font-medium text-gray-700">
                  <span>Processing document...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-full transition-all duration-300 shadow-lg"
                    style={{ width: `${uploadProgress}%` }}
                  >
                    <div className="h-full w-full bg-white/20 animate-pulse"></div>
                  </div>
                </div>
                {uploadProgress === 100 && (
                  <div className="flex items-center space-x-2 text-green-600 font-medium animate-fade-in">
                    <CheckCircle size={20} />
                    <span>Upload complete!</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Text Upload Tab */}
        {activeTab === 'text' && (
          <div className="space-y-4">
            <label className="label flex items-center space-x-2">
              <Sparkles className="text-blue-600" size={20} />
              <span>Enter your text</span>
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="input h-64 resize-none font-mono text-sm"
              placeholder="Paste your document text here..."
            />

            <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl">
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-600">Characters:</span>
                  <span className="font-bold text-gray-900">{text.length}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                  <span className="text-gray-600">Words:</span>
                  <span className="font-bold text-gray-900">{text.trim().split(/\s+/).filter(Boolean).length}</span>
                </div>
              </div>
              <button
                onClick={handleTextUpload}
                disabled={uploading || !text.trim()}
                className="btn-primary"
              >
                {uploading ? (
                  <>
                    <div className="spinner inline-block mr-2" style={{ width: '20px', height: '20px' }}></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Upload className="inline mr-2" size={20} />
                    <span>Upload Text</span>
                  </>
                )}
              </button>
            </div>

            {uploading && uploadProgress > 0 && (
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            )}
          </div>
        )}

        {/* MCQ File Upload Tab */}
        {activeTab === 'mcq' && (
          <div className="space-y-4">
            {!uploadedFile ? (
              <div
                {...mcqDropzone.getRootProps()}
                className={`relative border-4 border-dashed rounded-3xl p-16 text-center cursor-pointer transition-all duration-300 ${
                  mcqDropzone.isDragActive
                    ? 'border-emerald-500 bg-gradient-to-br from-emerald-50 to-green-50 scale-[1.02] shadow-xl'
                    : 'border-gray-300 hover:border-emerald-400 hover:bg-gradient-to-br hover:from-emerald-50/50 hover:to-green-50/50 hover:scale-[1.01]'
                }`}
              >
                <input {...mcqDropzone.getInputProps()} />
                <div className={`transition-all duration-300 ${mcqDropzone.isDragActive ? 'scale-110' : ''}`}>
                  <FileText
                    className={`mx-auto mb-6 ${mcqDropzone.isDragActive ? 'text-emerald-600 animate-bounce' : 'text-gray-400'}`}
                    size={64}
                  />
                  <p className="text-xl font-bold text-gray-700 mb-3">
                    {mcqDropzone.isDragActive ? '✨ Drop your MCQ file!' : '📝 Drag & drop MCQ file'}
                  </p>
                  <p className="text-gray-500 mb-4">or click to browse from your computer</p>
                  <div className="flex items-center justify-center space-x-4 text-sm text-gray-400">
                    <span className="badge bg-emerald-100 text-emerald-600">JSON</span>
                    <span className="badge bg-green-100 text-green-600">CSV</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="relative overflow-hidden bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-6 shadow-lg animate-slide-in-bottom">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-4 rounded-2xl shadow-lg">
                      <FileText className="text-white" size={32} />
                    </div>
                    <div>
                      <p className="font-bold text-lg text-gray-900">{uploadedFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {(uploadedFile.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={clearFile}
                    className="p-2 rounded-xl hover:bg-red-100 text-red-500 hover:text-red-700 transition-all hover:scale-110"
                  >
                    <X size={24} />
                  </button>
                </div>
              </div>
            )}

            {uploading && (
              <div className="space-y-3 animate-slide-in-bottom">
                <div className="flex items-center justify-between text-sm font-medium text-gray-700">
                  <span>Loading MCQs...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 via-green-500 to-teal-500 rounded-full transition-all duration-300 shadow-lg"
                    style={{ width: `${uploadProgress}%` }}
                  >
                    <div className="h-full w-full bg-white/20 animate-pulse"></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
