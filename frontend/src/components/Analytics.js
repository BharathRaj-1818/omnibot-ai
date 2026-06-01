import React from 'react';

const Analytics = ({ data, onClose }) => {
  if (!data) return null;

  return (
    <div className="bg-white border-b p-4 shadow-sm">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold text-gray-800">📊 Analytics</h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 font-bold"
        >
          ✕
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <p className="text-xs text-gray-600">Conversations</p>
          <p className="text-2xl font-bold text-blue-600">
            {data.total_conversations || 0}
          </p>
        </div>

        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-xs text-gray-600">Messages</p>
          <p className="text-2xl font-bold text-green-600">
            {data.total_messages || 0}
          </p>
        </div>

        <div className="bg-purple-50 p-3 rounded-lg">
          <p className="text-xs text-gray-600">Images</p>
          <p className="text-2xl font-bold text-purple-600">
            {data.total_images_generated || 0}
          </p>
        </div>

        <div className="bg-orange-50 p-3 rounded-lg">
          <p className="text-xs text-gray-600">Active Users</p>
          <p className="text-2xl font-bold text-orange-600">
            {data.active_users || 0}
          </p>
        </div>
      </div>

      {data.popular_personality && (
        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600">Popular Mode</p>
          <p className="font-semibold text-gray-800 capitalize">
            {data.popular_personality}
          </p>
        </div>
      )}
    </div>
  );
};

export default Analytics;