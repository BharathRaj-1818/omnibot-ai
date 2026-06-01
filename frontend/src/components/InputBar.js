import React, { useState, useRef } from 'react';
import { Send, Mic, Image } from 'lucide-react';

const InputBar = ({ onSendMessage, onImageGenerate, onVoiceInput, isLoading, personality }) => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceClick = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setMessage(transcript);
      setIsRecording(false);
    };

    recognition.onerror = () => {
      setIsRecording(false);
      alert('Voice recognition failed. Please try again.');
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.start();
  };

  const personalities = {
    friendly: 'Friendly',
    professional: 'Professional',
    creative: 'Creative',
  };

  return (
    <div className="bg-white border-t p-4 shadow-lg">
      <div className="flex items-center space-x-2">
        <button
          onClick={handleVoiceClick}
          className={`p-3 rounded-full transition-all ${
            isRecording
              ? 'bg-red-500 text-white animate-pulse'
              : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
          }`}
          title="Voice Input"
          disabled={isLoading}
        >
          <Mic className="w-5 h-5" />
        </button>

        <button
          onClick={onImageGenerate}
          className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors disabled:opacity-50"
          title="Generate Image"
          disabled={isLoading}
        >
          <Image className="w-5 h-5" />
        </button>

        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          disabled={isLoading}
        />

        <button
          onClick={handleSend}
          disabled={isLoading || !message.trim()}
          className="p-3 bg-blue-500 hover:bg-blue-600 text-white rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>

      <p className="text-xs text-center text-gray-500 mt-2">
        Mode: <span className="font-semibold">{personalities[personality]}</span>
      </p>
    </div>
  );
};

export default InputBar;