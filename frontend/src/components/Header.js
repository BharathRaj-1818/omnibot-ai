import React from 'react';
import { Smile, Briefcase, Sparkles, BarChart3, Settings } from 'lucide-react';

const Header = ({ personality, onPersonalityChange, onSettingsToggle, onAnalyticsToggle }) => {
  const personalities = {
    friendly: { icon: <Smile className="w-5 h-5" />, color: 'bg-blue-500', label: 'Friendly' },
    professional: { icon: <Briefcase className="w-5 h-5" />, color: 'bg-gray-600', label: 'Professional' },
    creative: { icon: <Sparkles className="w-5 h-5" />, color: 'bg-purple-500', label: 'Creative' },
  };

  return (
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
              onClick={() => onPersonalityChange(key)}
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
          onClick={onAnalyticsToggle}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Analytics"
        >
          <BarChart3 className="w-5 h-5 text-gray-600" />
        </button>

        <button
          onClick={onSettingsToggle}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Settings"
        >
          <Settings className="w-5 h-5 text-gray-600" />
        </button>
      </div>
    </header>
  );
};

export default Header;