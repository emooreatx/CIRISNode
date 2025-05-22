"use client";
import React, { useState, useEffect } from 'react';

interface HealthStatusData {
  status: string;
  version: string;
  pubkey: string;
}

const HealthStatus: React.FC = () => {
  const [health, setHealth] = useState<HealthStatusData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealthStatus = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/health');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: HealthStatusData = await response.json();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setHealth(null);
      } finally {
        setLoading(false);
      }
    };

    fetchHealthStatus();
  }, []);

  if (loading) {
    return <div className="text-center py-4">Loading health status...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  }

  if (!health) {
    return <div className="text-gray-500 text-center py-4">No health status available.</div>;
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Health Status</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">Current status of CIRISNode service.</p>
      </div>
      <div className="border-t border-gray-200">
        <dl>
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Status</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{health.status}</dd>
          </div>
          <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Version</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{health.version}</dd>
          </div>
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Public Key</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 truncate">{health.pubkey}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
};

export default HealthStatus;
