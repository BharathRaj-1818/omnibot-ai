import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { 
  Send, Mic, Image, Settings, BarChart3, Languages, 
  Smile, Briefcase, Sparkles, Download, Volume2 
} from 'lucide-react';
import axios from 'axios';
import ChatPage from './pages/ChatPage';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [personality, setPersonality] = useState('friendly');
  const [autoTranslate, setAutoTranslate] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Welcome message
    setMessages([{
      type: 'bot',
      content: 'Hello! 👋 I\'m OmniBot, your intelligent AI assistant. I can chat in multiple languages, generate images, and adapt my personality to your needs. How can I help you today?',
      timestamp: new Date()
    }]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: inputMessage,
        user_id: 'web-user-' + Date.now(),
        personality_mode: personality,
        auto_translate: autoTranslate
      });

      const botMessage = {
        type: 'bot',
        content: response.data.response,
        timestamp: new Date(),
        language: response.data.detected_language
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'bot',
        content: '❌ Sorry, I encountered an error. Please try again!',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const generateImage = async () => {
  if (!inputMessage.trim()) {
    alert("Please enter an image description in the input box.");
    return;
  }

  const statusMessage = {
    type: 'bot',
    content: '🎨 Generating your image... This may take a moment!',
    timestamp: new Date()
  };

  setMessages(prev => [...prev, statusMessage]);

  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/generate-image`,
      {
        prompt: inputMessage,
        user_id: 'web-user'
      },
      {
        responseType: 'blob'
      }
    );

    const imageUrl = URL.createObjectURL(response.data);

    const imageMessage = {
      type: 'bot',
      content: `✅ Generated image for: "${inputMessage}"`,
      image: imageUrl,
      timestamp: new Date()
    };

    setMessages(prev => [...prev.slice(0, -1), imageMessage]);

    setInputMessage('');

  } catch (error) {
    console.error('Error generating image:', error);

    const errorMessage = {
      type: 'bot',
      content: '❌ Image generation failed. Please check backend logs.',
      timestamp: new Date()
    };

    setMessages(prev => [...prev.slice(0, -1), errorMessage]);
  }
};

  const handleVoiceInput = async () => {

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert('Speech recognition is not supported in this browser.');
    return;
  }

  const recognition = new SpeechRecognition();

  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  recognition.onstart = () => {
    setIsRecording(true);
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setInputMessage(transcript);
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    alert(`Voice recognition failed: ${event.error}`);
    setIsRecording(false);
  };

  recognition.onend = () => {
    setIsRecording(false);
  };

  recognition.start();
};

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analytics`);
      setAnalytics(response.data);
      setShowAnalytics(true);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const personalities = {
    friendly: { icon: <Smile className="w-5 h-5" />, color: 'bg-blue-500', label: 'Friendly' },
    professional: { icon: <Briefcase className="w-5 h-5" />, color: 'bg-gray-600', label: 'Professional' },
    creative: { icon: <Sparkles className="w-5 h-5" />, color: 'bg-purple-500', label: 'Creative' }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
            AI
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800">OmniBot</h1>
            <p className="text-xs text-gray-500">Multi-Platform AI Assistant</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Personality Selector */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            {Object.entries(personalities).map(([key, { icon, color, label }]) => (
              <button
                key={key}
                onClick={() => setPersonality(key)}
                className={`px-3 py-2 rounded-md transition-all ${
                  personality === key ? `${color} text-white` : 'text-gray-600 hover:bg-gray-200'
                }`}
                title={label}
              >
                {icon}
              </button>
            ))}
          </div>

          {/* Action Buttons */}
          <button
            onClick={loadAnalytics}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Analytics"
          >
            <BarChart3 className="w-5 h-5 text-gray-600" />
          </button>
          
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Settings"
          >
            <Settings className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-white border-b p-4 shadow-sm">
          <h3 className="font-semibold mb-3 text-gray-800">Settings</h3>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoTranslate}
                onChange={(e) => setAutoTranslate(e.target.checked)}
                className="w-4 h-4 text-blue-500"
              />
              <span className="text-sm text-gray-700">Auto-translate messages</span>
            </label>
          </div>
        </div>
      )}

      {/* Analytics Panel */}
      {showAnalytics && analytics && (
        <div className="bg-white border-b p-4 shadow-sm">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-gray-800">Analytics</h3>
            <button onClick={() => setShowAnalytics(false)} className="text-gray-500 hover:text-gray-700">
              ✕
            </button>
          </div>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-xs text-gray-600">Conversations</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.total_conversations}</p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <p className="text-xs text-gray-600">Messages</p>
              <p className="text-2xl font-bold text-green-600">{analytics.total_messages}</p>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <p className="text-xs text-gray-600">Images</p>
              <p className="text-2xl font-bold text-purple-600">{analytics.total_images_generated}</p>
            </div>
            <div className="bg-orange-50 p-3 rounded-lg">
              <p className="text-xs text-gray-600">Active Users</p>
              <p className="text-2xl font-bold text-orange-600">{analytics.active_users}</p>
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-800 shadow-md'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.image && (
                <img
                  src={message.image}
                  alt="Generated"
                  className="mt-2 rounded-lg max-w-full"
                />
              )}
              <p className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-400'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl px-4 py-3 shadow-md">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t p-4 shadow-lg">
        <div className="flex items-center space-x-2">
          <button
            onClick={handleVoiceInput}
            className={`p-3 rounded-full transition-all ${
              isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
            }`}
            title="Voice Input"
          >
            <Mic className="w-5 h-5" />
          </button>

          <button
            onClick={generateImage}
            className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"
            title="Generate Image"
          >
            <Image className="w-5 h-5" />
          </button>

          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />

          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="p-3 bg-blue-500 hover:bg-blue-600 text-white rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <p className="text-xs text-center text-gray-500 mt-2">
          Current mode: <span className="font-semibold">{personalities[personality].label}</span>
        </p>
      </div>
    </div>
  );
}

export default App;
