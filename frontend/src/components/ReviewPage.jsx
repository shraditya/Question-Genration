import React, { useEffect, useState } from 'react';
import { Edit2, Trash2, CheckCircle, AlertTriangle, RefreshCcw, Upload } from 'lucide-react';

export default function ReviewPage() {
    const [mcqs, setMcqs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);

    const fetchMcqs = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/mcqs');
            const data = await res.json();
            setMcqs(data.mcqs || []);
        } catch (err) {
            console.error('Failed to fetch MCQs', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMcqs();
    }, []);

    const handleFileUpload = async (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const res = await fetch('http://localhost:8000/api/upload_mcqs', {
                method: 'POST',
                body: formData,
            });
            const data = await res.json();
            if (res.ok) {
                alert(data.message || 'File uploaded and processed successfully.');
                fetchMcqs();
            } else {
                alert(data.detail || 'Upload failed');
            }
        } catch (err) {
            alert('Error uploading document');
        } finally {
            setIsUploading(false);
            e.target.value = null; // reset input
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Are you sure you want to delete this question?')) return;
        try {
            await fetch(`http://localhost:8000/api/mcqs/${id}`, {
                method: 'DELETE'
            });
            fetchMcqs();
        } catch (err) {
            alert('Failed to delete');
        }
    };

    return (
        <div>
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1 className="page-title">Tag & Review</h1>
                    <p className="page-subtitle">Upload MCQ documents (JSON/CSV) to run auto-tagging and similarity checks against the database.</p>
                </div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <input
                        type="file"
                        id="mcq-upload"
                        style={{ display: 'none' }}
                        onChange={handleFileUpload}
                        accept=".csv,.json"
                    />
                    <label htmlFor="mcq-upload" className="btn btn-primary" style={{ cursor: 'pointer', margin: 0, width: 'auto' }}>
                        <Upload size={16} /> {isUploading ? 'Processing...' : 'Upload MCQ JSON/CSV'}
                    </label>
                    <button className="btn btn-outline" onClick={fetchMcqs} disabled={loading}>
                        <RefreshCcw size={16} /> Refresh
                    </button>
                </div>
            </div>

            {loading && mcqs.length === 0 && <div style={{ padding: '2rem' }}>Loading questions...</div>}

            {!loading && mcqs.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>No Questions to Review</h3>
                    <p className="page-subtitle">Upload a JSON/CSV file above, or use the Generate tab to create some.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {mcqs.map((mcq, idx) => (
                        <div key={mcq.id || idx} className="card" style={{ position: 'relative' }}>
                            {/* Header / Meta */}
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
                                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                                    <span style={{ fontWeight: 600, color: 'var(--primary)' }}>ID #{mcq.id}</span>
                                    <span style={{ fontSize: '0.875rem', padding: '0.25rem 0.5rem', backgroundColor: '#f3f4f6', borderRadius: '4px' }}>
                                        {mcq.category || mcq.tags?.[0] || 'General'}
                                    </span>
                                    <span style={{ fontSize: '0.875rem', padding: '0.25rem 0.5rem', backgroundColor: '#f3f4f6', borderRadius: '4px' }}>
                                        {mcq.difficulty || 'Medium'}
                                    </span>
                                    {mcq.similarity_status === 'Duplicate' ? (
                                        <span style={{ fontSize: '0.875rem', padding: '0.25rem 0.5rem', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                            <AlertTriangle size={14} /> Duplicate
                                        </span>
                                    ) : mcq.similarity_status === 'Similar' ? (
                                        <span style={{ fontSize: '0.875rem', padding: '0.25rem 0.5rem', backgroundColor: '#fef3c7', color: '#92400e', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                            <AlertTriangle size={14} /> Similar
                                        </span>
                                    ) : (
                                        <span style={{ fontSize: '0.875rem', padding: '0.25rem 0.5rem', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                            <CheckCircle size={14} /> Unique
                                        </span>
                                    )}
                                </div>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button className="btn btn-outline" style={{ padding: '0.5rem' }} title="Edit (Coming soon)">
                                        <Edit2 size={16} />
                                    </button>
                                    <button className="btn btn-outline" style={{ padding: '0.5rem', color: '#ef4444', borderColor: '#fee2e2' }} title="Delete" onClick={() => handleDelete(mcq.id)}>
                                        <Trash2 size={16} />
                                    </button>
                                </div>
                            </div>

                            {/* Content */}
                            <div style={{ marginBottom: '1.5rem' }}>
                                <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>{mcq.question}</h3>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                    {Object.entries(mcq.options || {}).map(([key, value]) => {
                                        const isCorrect = mcq.correct_answer === key;
                                        return (
                                            <div
                                                key={key}
                                                style={{
                                                    padding: '0.75rem',
                                                    border: `1px solid ${isCorrect ? 'var(--primary)' : 'var(--border-color)'}`,
                                                    borderRadius: '6px',
                                                    backgroundColor: isCorrect ? 'var(--primary-light)' : 'white',
                                                    display: 'flex',
                                                    gap: '1rem'
                                                }}
                                            >
                                                <span style={{ fontWeight: 600, color: isCorrect ? 'var(--primary)' : 'var(--text-muted)' }}>{key}.</span>
                                                <span>{value}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Footer / Explanation */}
                            {
                                mcq.explanation && (
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', backgroundColor: '#f9fafb', padding: '1rem', borderRadius: '6px' }}>
                                        <strong>Explanation:</strong> {mcq.explanation}
                                    </div>
                                )
                            }
                            {
                                mcq.tags && mcq.tags.length > 0 && (
                                    <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                        <strong style={{ fontSize: '0.875rem' }}>Tags:</strong>
                                        {mcq.tags.map(t => (
                                            <span key={t} style={{ fontSize: '0.75rem', color: 'var(--primary)', border: '1px solid var(--primary-light)', padding: '0.1rem 0.4rem', borderRadius: '12px' }}>
                                                {t}
                                            </span>
                                        ))}
                                    </div>
                                )
                            }
                        </div>
                    ))}
                </div>
            )
            }
        </div >
    );
}
