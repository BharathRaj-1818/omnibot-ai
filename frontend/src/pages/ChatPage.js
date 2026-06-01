import React, { useState, useEffect, useRef } from 'react';
import { Header, ChatMessage, InputBar, Analytics, Settings, LoadingIndicator } from '../components';
import { chatAPI } from '../services/api';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [personality, setPersonality] = useState('friendly');
  const [autoTranslate, setAutoTranslate] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  
  const messagesEndRef = useRef(null);

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

    // Set user ID
    if (!localStorage.getItem('userId')) {
      localStorage.setItem('userId', 'user-' + Date.now());
    }
  }, []);

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      type: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatAPI.send(text, personality, autoTranslate);

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

  const handleGenerateImage = async () => {
    const prompt = window.prompt('Enter image description:');
    if (!prompt) return;

    const statusMessage = {
      type: 'bot',
      content: '🎨 Generating your image... This may take a moment!',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, statusMessage]);

    try {
      const response = await chatAPI.generateImage(prompt);
      const imageUrl = URL.createObjectURL(response.data);
      
      const imageMessage = {
        type: 'bot',
        content: '✅ Here\'s your generated image!',
        image: imageUrl,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev.slice(0, -1), imageMessage]);
    } catch (error) {
      console.error('Error generating image:', error);
      const errorMessage = {
        type: 'bot',
        content: '❌ Image generation failed. This feature may be disabled on this server.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev.slice(0, -1), errorMessage]);
    }
  };

  const handleLoadAnalytics = async () => {
    try {
      const response = await chatAPI.getAnalytics();
      setAnalytics(response.data);
      setShowAnalytics(true);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <Header
        personality={personality}
        onPersonalityChange={setPersonality}
        onSettingsToggle={() => setShowSettings(!showSettings)}
        onAnalyticsToggle={handleLoadAnalytics}
      />

      {/* Settings Panel */}
      {showSettings && (
        <Settings
          autoTranslate={autoTranslate}
          onAutoTranslateChange={setAutoTranslate}
        />
      )}

      {/* Analytics Panel */}
      {showAnalytics && (
        <Analytics
          data={analytics}
          onClose={() => setShowAnalytics(false)}
        />
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <ChatMessage
            key={index}
            message={message}
            isUser={message.type === 'user'}
          />
        ))}

        {isLoading && <LoadingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <InputBar
        onSendMessage={handleSendMessage}
        onImageGenerate={handleGenerateImage}
        isLoading={isLoading}
        personality={personality}
      />
    </div>
  );
};

export default ChatPage;