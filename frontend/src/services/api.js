import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Chat endpoints
export const chatAPI = {
  send: (message, personalityMode = 'friendly', autoTranslate = false) =>
    api.post('/api/chat', {
      message,
      personality_mode: personalityMode,
      auto_translate: autoTranslate,
      user_id: localStorage.getItem('userId') || 'web-user',
    }),

  getAnalytics: () =>
    api.get('/api/analytics'),

  getLanguages: () =>
    api.get('/api/languages'),

  translate: (text, targetLanguage, sourceLanguage = 'auto') =>
    api.post('/api/translate', null, {
      params: {
        text,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      },
    }),

  generateImage: (prompt, width = 512, height = 512) =>
    api.post(
      '/api/generate-image',
      {
        prompt,
        width,
        height,
        user_id: localStorage.getItem('userId') || 'web-user',
      },
      { responseType: 'blob' }
    ),

  textToSpeech: (text, language = 'en') =>
    api.post(
      '/api/text-to-speech',
      null,
      {
        params: { text, language },
        responseType: 'blob',
      }
    ),

  health: () =>
    api.get('/health'),
};

export default api;