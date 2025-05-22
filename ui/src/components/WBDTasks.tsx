"use client";
import React, { useState, useEffect } from 'react';

interface WBDTaskData {
  id: number;
  agent_task_id: string;
  payload: string;
  status: string;
  created_at: string;
  decision?: string;
  comment?: string;
}

const WBDTasks: React.FC = () => {
  const [tasks, setTasks] = useState<WBDTaskData[]>([]);
  const [stateFilter, setStateFilter] = useState<string>('');
  const [sinceFilter, setSinceFilter] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [resolveTaskId, setResolveTaskId] = useState<number | null>(null);
  const [resolveDecision, setResolveDecision] = useState<string>('approve');
  const [resolveComment, setResolveComment] = useState<string>('');

  const fetchTasks = async () => {
    try {
      setLoading(true);
      let url = '/api/v1/wbd/tasks';
      const params = new URLSearchParams();
      if (stateFilter) params.append('state', stateFilter);
      if (sinceFilter) params.append('since', sinceFilter);
      if (params.toString()) url += `?${params.toString()}`;

      const headers: HeadersInit = {};
      const response = await fetch(url, { headers });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail}`);
      }
      const data = await response.json(); // Expecting {"tasks": [...]}
      setTasks(data.tasks || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [stateFilter, sinceFilter]);

  const handleResolveTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (resolveTaskId === null) return;

    setLoading(true);
    try {
      const headers: HeadersInit = { 'Content-Type': 'application/json' };
      const response = await fetch(`/api/v1/wbd/tasks/${resolveTaskId}/resolve`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ decision: resolveDecision, comment: resolveComment }),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail}`);
      }
      setResolveTaskId(null);
      setResolveComment('');
      fetchTasks(); // Refresh tasks list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading && tasks.length === 0) { // Show initial loading only
    return <div className="text-center py-4">Loading WBD tasks...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg mt-6">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Wisdom-Based Deferral (WBD) Tasks</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">Manage and resolve WBD tasks.</p>
      </div>
      <div className="border-t border-gray-200">
        <div className="px-4 py-5 sm:p-6">
          <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label htmlFor="stateFilter" className="block text-sm font-medium text-gray-700">
                Filter by State
              </label>
              <select
                id="stateFilter"
                value={stateFilter}
                onChange={(e) => setStateFilter(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              >
                <option value="">All</option>
                <option value="open">Open</option>
                <option value="resolved">Resolved</option>
                <option value="sla_breached">SLA Breached</option>
              </select>
            </div>
            <div>
              <label htmlFor="sinceFilter" className="block text-sm font-medium text-gray-700">
                Since Date (YYYY-MM-DD)
              </label>
              <input
                type="date"
                id="sinceFilter"
                value={sinceFilter}
                onChange={(e) => setSinceFilter(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              />
            </div>
            <button onClick={fetchTasks} disabled={loading} className="py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
              {loading ? 'Refreshing...' : 'Refresh Tasks'}
            </button>
          </div>

          {resolveTaskId !== null && (
            <form onSubmit={handleResolveTask} className="mb-6 p-4 border rounded-md bg-gray-50">
              <h4 className="text-md font-semibold text-gray-800 mb-2">Resolve Task ID: {resolveTaskId}</h4>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label htmlFor="resolveDecision" className="block text-sm font-medium text-gray-700">Decision</label>
                  <select id="resolveDecision" value={resolveDecision} onChange={(e) => setResolveDecision(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                    <option value="approve">Approve</option>
                    <option value="reject">Reject</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="resolveComment" className="block text-sm font-medium text-gray-700">Comment (optional)</label>
                  <textarea id="resolveComment" value={resolveComment} onChange={(e) => setResolveComment(e.target.value)} rows={3} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"></textarea>
                </div>
                <div className="flex justify-end space-x-2">
                  <button type="button" onClick={() => setResolveTaskId(null)} className="py-2 px-4 border rounded-md text-sm">Cancel</button>
                  <button type="submit" disabled={loading} className="py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
                    {loading ? 'Submitting...' : 'Submit Resolution'}
                  </button>
                </div>
              </div>
            </form>
          )}

          {tasks.length === 0 && !loading ? (
            <div className="text-center py-4 text-gray-500">No WBD tasks found for the selected filters.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent Task ID</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payload</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {tasks.map((task) => (
                    <tr key={task.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{task.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.agent_task_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          task.status === 'open' ? 'bg-yellow-100 text-yellow-800' :
                          task.status === 'resolved' ? 'bg-green-100 text-green-800' :
                          task.status === 'sla_breached' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {task.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(task.created_at).toLocaleString()}</td>
                      <td className="px-6 py-4 text-sm text-gray-500 truncate max-w-xs" title={task.payload}>{task.payload}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {task.status === 'open' && (
                          <button onClick={() => setResolveTaskId(task.id)} className="text-indigo-600 hover:text-indigo-900">Resolve</button>
                        )}
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

export default WBDTasks;
