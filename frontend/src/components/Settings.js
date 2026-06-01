import React from 'react';

const Settings = ({ autoTranslate, onAutoTranslateChange }) => {
  return (
    <div className="bg-white border-b p-4 shadow-sm">
      <h3 className="font-semibold mb-3 text-gray-800">⚙️ Settings</h3>

      <div className="flex items-center space-x-4">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={autoTranslate}
            onChange={(e) => onAutoTranslateChange(e.target.checked)}
            className="w-4 h-4 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Auto-translate messages</span>
        </label>
      </div>

      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-blue-700">
          💡 Enable auto-translate to automatically detect and translate messages in other languages.
        </p>
      </div>
    </div>
  );
};

export default Settings;