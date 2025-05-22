"use client";
import React, { useState } from 'react';

const BenchmarkRunner: React.FC = () => {
  const [scenarioId, setScenarioId] = useState<string>('');
  const [chaosLevel, setChaosLevel] = useState<number | ''>('');
  const [serviceProvider, setServiceProvider] = useState<string>('openAI');
  const [model, setModel] = useState<string>('gpt-3.5-turbo');
  const [jobId, setJobId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const serviceProviders = [
    { id: 'openAI', name: 'OpenAI', models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'] },
    { id: 'xAI', name: 'xAI', models: ['grok-1', 'grok-2'] },
    { id: 'gemini', name: 'Gemini', models: ['gemini-1.0', 'gemini-1.5'] },
    { id: 'ollama', name: 'Ollama', models: ['llama-2', 'llama-3'] },
    { id: 'anthropic', name: 'Anthropic', models: ['claude-2', 'claude-3'] },
    { id: 'mistral', name: 'Mistral', models: ['mistral-small', 'mistral-large'] },
  ];

  const handleRunBenchmark = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setJobId(null);

    try {
      const body: { scenario_id?: string; chaos_level?: number; service_provider?: string; model?: string } = {};
      if (scenarioId) body.scenario_id = scenarioId;
      if (chaosLevel !== '') body.chaos_level = Number(chaosLevel);
      if (serviceProvider) body.service_provider = serviceProvider;
      if (model) body.model = model;

      const response = await fetch('/api/v1/benchmarks/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('authToken') && {'Authorization': `Bearer ${localStorage.getItem('authToken')}`})
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail}`);
      }

      const data = await response.json(); // Expecting {"job_id": "some_id"}
      setJobId(data.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleServiceProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const providerId = e.target.value;
    setServiceProvider(providerId);
    const provider = serviceProviders.find(p => p.id === providerId);
    if (provider && provider.models.length > 0) {
      setModel(provider.models[0]);
    } else {
      setModel('');
    }
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg mt-6">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Run Benchmark (HE-300)</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">Initiate a new HE-300 benchmark run with selected AI service.</p>
      </div>
      <div className="border-t border-gray-200">
        <form onSubmit={handleRunBenchmark} className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="scenarioId" className="block text-sm font-medium text-gray-700">
                Scenario ID (e.g., HE-300-1)
              </label>
              <input
                type="text"
                id="scenarioId"
                value={scenarioId}
                onChange={(e) => setScenarioId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                placeholder="e.g., HE-300-1"
                required
              />
            </div>
            <div>
              <label htmlFor="chaosLevel" className="block text-sm font-medium text-gray-700">
                Chaos Level (0-5, optional)
              </label>
              <input
                type="number"
                id="chaosLevel"
                value={chaosLevel}
                min="0"
                max="5"
                onChange={(e) => setChaosLevel(e.target.value === '' ? '' : Number(e.target.value))}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                placeholder="e.g., 1"
              />
            </div>
            <div>
              <label htmlFor="serviceProvider" className="block text-sm font-medium text-gray-700">
                AI Service Provider
              </label>
              <select
                id="serviceProvider"
                value={serviceProvider}
                onChange={handleServiceProviderChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              >
                {serviceProviders.map(provider => (
                  <option key={provider.id} value={provider.id}>{provider.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="model" className="block text-sm font-medium text-gray-700">
                Model
              </label>
              <select
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              >
                {serviceProviders.find(p => p.id === serviceProvider)?.models.map(modelName => (
                  <option key={modelName} value={modelName}>{modelName}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="mt-6">
            <button
              type="submit"
              disabled={loading || !scenarioId}
              className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
                loading || !scenarioId ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
            >
              {loading ? 'Running...' : 'Run Benchmark'}
            </button>
          </div>
          {error && (
            <div className="mt-4 text-red-500 text-sm">
              Error: {error}
            </div>
          )}
          {jobId && (
            <div className="mt-4 text-green-500 text-sm">
              Benchmark started successfully. Job ID: {jobId}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default BenchmarkRunner;
