import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2 } from 'lucide-react';

export default function GeneratePage({ onComplete }) {
    const [topic, setTopic] = useState('');
    const [details, setDetails] = useState('');
    const [numQuestions, setNumQuestions] = useState(5);
    const [optionsPerQuestion, setOptionsPerQuestion] = useState(4);
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [uploadedFileName, setUploadedFileName] = useState('');

    const handleFileUpload = async (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        setFile(selectedFile);
        setIsUploading(true);

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const res = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData,
            });
            const data = await res.json();
            if (res.ok) {
                setUploadedFileName(selectedFile.name);
            } else {
                alert(data.detail || 'Upload failed');
            }
        } catch (err) {
            alert('Error uploading document');
        } finally {
            setIsUploading(false);
        }
    };

    const handleGenerate = async () => {
        if (!uploadedFileName) {
            alert('Please upload a document to generate questions from.');
            return;
        }

        setIsGenerating(true);
        try {
            const res = await fetch('http://localhost:8000/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic,
                    additional_details: details,
                    num_questions: numQuestions,
                    options_per_question: optionsPerQuestion
                })
            });

            const data = await res.json();
            if (res.ok) {
                onComplete();
            } else {
                alert(data.detail || 'Generation failed');
            }
        } catch (err) {
            alert('Error generating questions');
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Generate Questions</h1>
                <p className="page-subtitle">Create new multiple-choice questions based on topics and documents.</p>
            </div>

            <div className="layout-grid">
                {/* Left Column: Form */}
                <div className="card">
                    <div className="form-group">
                        <label className="form-label">Topic</label>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="Enter a topic or subject"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                            />
                            <button className="btn btn-outline" style={{ whiteSpace: 'nowrap' }}>New Topic</button>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Additional Details (Optional)</label>
                        <textarea
                            className="form-textarea"
                            placeholder="Provide more details about the topic or specific areas to focus on..."
                            value={details}
                            onChange={(e) => setDetails(e.target.value)}
                        ></textarea>
                    </div>

                    <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem' }}>
                        <div style={{ flex: 1 }}>
                            <label className="form-label">Number of Questions: {numQuestions}</label>
                            <div className="slider-container">
                                <input
                                    type="range"
                                    min="1"
                                    max="30"
                                    value={numQuestions}
                                    onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                                />
                            </div>
                        </div>

                        <div style={{ flex: 1 }}>
                            <label className="form-label">Options per Question: {optionsPerQuestion}</label>
                            <div className="slider-container">
                                <input
                                    type="range"
                                    min="2"
                                    max="6"
                                    value={optionsPerQuestion}
                                    onChange={(e) => setOptionsPerQuestion(parseInt(e.target.value))}
                                />
                            </div>
                        </div>
                    </div>

                    <button
                        className="btn btn-primary"
                        onClick={handleGenerate}
                        disabled={isGenerating || isUploading}
                    >
                        <Sparkles size={18} />
                        {isGenerating ? 'Generating...' : 'Generate Questions'}
                    </button>
                </div>

                {/* Right Column: Docs & Tips */}
                <div>
                    <div className="card" style={{ marginBottom: '1.5rem' }}>
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                            <FileText size={18} color="var(--primary)" /> Available Documents
                        </h3>

                        {uploadedFileName ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', fontWeight: '500' }}>
                                <CheckCircle2 size={18} />
                                <span>{uploadedFileName}</span>
                            </div>
                        ) : (
                            <div>
                                <input
                                    type="file"
                                    id="doc-upload"
                                    style={{ display: 'none' }}
                                    onChange={handleFileUpload}
                                    accept=".pdf,.txt,.docx"
                                />
                                <label htmlFor="doc-upload" className="btn btn-outline" style={{ width: '100%', marginBottom: '1rem' }}>
                                    <Upload size={18} />
                                    {isUploading ? 'Uploading...' : 'Upload Document'}
                                </label>
                                <p className="page-subtitle" style={{ textAlign: 'center' }}>Upload PDF, DOCX, or TXT.</p>
                            </div>
                        )}
                    </div>

                    <div className="card">
                        <h3 style={{ marginBottom: '1rem' }}>Tips</h3>
                        <ul className="tips-list">
                            <li>Be specific with your topic for better results</li>
                            <li>Add details to focus on specific aspects of the topic</li>
                            <li>Select or upload relevant documents to provide context for generation</li>
                            <li>The optimal number of options per question is typically 4</li>
                            <li>Generated questions will need to be reviewed before use</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Keep the import sparkle locally here if lucide doesn't load it naturally from the file scope
const Sparkles = ({ size }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" /></svg>
);
