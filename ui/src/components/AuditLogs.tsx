"use client";
import React, { useState, useEffect } from 'react';

interface AuditLogEntryData {
  id: number;
  timestamp: string;
  actor: string;
  event_type: string;
  payload_sha256: string;
  raw_json: string;
}

const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEntryData[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [fromDateFilter, setFromDateFilter] = useState<string>('');
  const [toDateFilter, setToDateFilter] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      let url = '/api/v1/audit/logs';
      const params = new URLSearchParams();
      if (typeFilter) params.append('type', typeFilter);
      if (fromDateFilter) params.append('from_date', fromDateFilter);
      if (toDateFilter) params.append('to_date', toDateFilter);
      if (params.toString()) url += `?${params.toString()}`;

      const token = localStorage.getItem('authToken');
      const headers: HeadersInit = {
        Authorization: "Bearer simple-static-token", // Include the static token
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(url, { headers });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail}`);
      }
      const data = await response.json(); // Expecting {"logs": [...]}
      setLogs(data.logs || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [typeFilter, fromDateFilter, toDateFilter]);

  if (loading && logs.length === 0) { // Show initial loading only
    return <div className="text-center py-4">Loading audit logs...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg mt-6">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Audit Logs</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">View immutable logs of all system events.</p>
      </div>
      <div className="border-t border-gray-200">
        <div className="px-4 py-5 sm:p-6">
          <div className="mb-4 grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div>
              <label htmlFor="typeFilter" className="block text-sm font-medium text-gray-700">
                Event Type
              </label>
              <input
                type="text"
                id="typeFilter"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                placeholder="e.g., benchmark_run"
              />
            </div>
            <div>
              <label htmlFor="fromDateFilter" className="block text-sm font-medium text-gray-700">
                From Date
              </label>
              <input
                type="date"
                id="fromDateFilter"
                value={fromDateFilter}
                onChange={(e) => setFromDateFilter(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              />
            </div>
            <div>
              <label htmlFor="toDateFilter" className="block text-sm font-medium text-gray-700">
                To Date
              </label>
              <input
                type="date"
                id="toDateFilter"
                value={toDateFilter}
                onChange={(e) => setToDateFilter(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              />
            </div>
            <button onClick={fetchLogs} disabled={loading} className="py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
              {loading ? 'Refreshing...' : 'Refresh Logs'}
            </button>
          </div>
          {logs.length === 0 && !loading ? (
            <div className="text-center py-4 text-gray-500">No audit logs found for the selected filters.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actor</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Event Type</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payload SHA256</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details (JSON)</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{log.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(log.timestamp).toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{log.actor}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{log.event_type}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 truncate max-w-xs" title={log.payload_sha256}>{log.payload_sha256}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <pre className="whitespace-pre-wrap max-w-md overflow-auto bg-gray-100 p-2 rounded text-xs">{JSON.stringify(JSON.parse(log.raw_json), null, 2)}</pre>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;
