import React from 'react';

const ChatMessage = ({ message, isUser }) => {
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-white text-gray-800 shadow-md'
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        {message.image && (
          <img
            src={message.image}
            alt="Generated"
            className="mt-2 rounded-lg max-w-full"
          />
        )}
        <p
          className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-400'
          }`}
        >
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
};

export default ChatMessage;