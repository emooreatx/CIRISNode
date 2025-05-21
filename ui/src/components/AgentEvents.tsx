"use client";
import React, { useState } from 'react';

interface AgentEventResponse {
  status: string;
  event_id: number;
  message: string;
}

const AgentEvents: React.FC = () => {
  const [agentUid, setAgentUid] = useState<string>('');
  const [eventJson, setEventJson] = useState<string>('');
  const [response, setResponse] = useState<AgentEventResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handlePushEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agentUid || !eventJson) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      let parsedEventJson;
      try {
        parsedEventJson = JSON.parse(eventJson);
      } catch (parseError) { // Changed variable name to avoid conflict
        console.error("JSON Parse Error:", parseError);
        throw new Error('Invalid JSON format for event data. Please ensure it is a valid JSON object.');
      }

      const body = {
        agent_uid: agentUid,
        event_json: parsedEventJson
      };

      const res = await fetch('/api/v1/agent/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('authToken') && {'Authorization': `Bearer ${localStorage.getItem('authToken')}`})
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Unknown error occurred' }));
        throw new Error(`HTTP error! status: ${res.status} - ${errorData.detail}`);
      }

      const data = await res.json();
      setResponse(data);
      setAgentUid(''); // Clear fields on success
      setEventJson('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg mt-6">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Agent Events</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">Push Task/Thought/Action events from agents for observability.</p>
      </div>
      <div className="border-t border-gray-200">
        <form onSubmit={handlePushEvent} className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label htmlFor="agentUid" className="block text-sm font-medium text-gray-700">
                Agent UID
              </label>
              <input
                type="text"
                id="agentUid"
                value={agentUid}
                onChange={(e) => setAgentUid(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                placeholder="Enter unique identifier for the agent"
                required
              />
            </div>
            <div>
              <label htmlFor="eventJson" className="block text-sm font-medium text-gray-700">
                Event JSON
              </label>
              <textarea
                id="eventJson"
                value={eventJson}
                onChange={(e) => setEventJson(e.target.value)}
                rows={5}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                placeholder='Enter event data in JSON format, e.g., {"type": "Task", "data": {"id": "task_123", "description": "Sample task"}}'
                required
              />
            </div>
          </div>
          <div className="mt-6">
            <button
              type="submit"
              disabled={loading || !agentUid || !eventJson}
              className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
                loading || !agentUid || !eventJson ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
            >
              {loading ? 'Pushing...' : 'Push Event'}
            </button>
          </div>
          {error && (
            <div className="mt-4 text-red-500 text-sm">
              Error: {error}
            </div>
          )}
          {response && (
            <div className="mt-4 text-green-500 text-sm">
              Event pushed successfully. Event ID: {response.event_id}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default AgentEvents;
