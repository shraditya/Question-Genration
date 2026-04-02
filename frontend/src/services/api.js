import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Get configuration
export const getConfig = async () => {
  const response = await api.get('/config');
  return response.data;
};

// Upload text document
export const uploadText = async (text) => {
  const response = await api.post('/upload-text', { text });
  return response.data;
};

// Upload file
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload-file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Generate MCQs
export const generateMCQs = async (numQuestions = 10) => {
  const response = await api.post('/generate-mcqs', { num_questions: numQuestions });
  return response.data;
};

// Get current MCQs
export const getMCQs = async () => {
  const response = await api.get('/mcqs');
  return response.data;
};

// Auto-tag MCQs
export const autoTagMCQs = async (mcqs) => {
  const response = await api.post('/auto-tag', { mcqs });
  return response.data;
};

// Check similarity
export const checkSimilarity = async (mcqs, threshold = 0.75) => {
  const response = await api.post('/similarity-check', { mcqs, threshold });
  return response.data;
};

// Refine MCQs
export const refineMCQs = async (mcqs, feedback) => {
  const response = await api.post('/refine-mcqs', { mcqs, feedback });
  return response.data;
};

// Upload MCQ file
export const uploadMCQFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload-mcq-file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Export MCQs
export const exportMCQs = async (mcqs, format = 'json') => {
  const response = await api.post('/export', { mcqs, format }, {
    responseType: 'blob',
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `mcqs.${format}`);
  document.body.appendChild(link);
  link.click();
  link.remove();

  return { success: true };
};

// Clear all data
export const clearData = async () => {
  const response = await api.delete('/clear');
  return response.data;
};

export default api;
