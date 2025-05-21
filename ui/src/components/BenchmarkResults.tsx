"use client";
import React, { useState } from 'react';

interface BenchmarkResultData {
  id: string;
  response: string;
  timestamp: string;
}

interface SignedBenchmarkResult {
  result: BenchmarkResultData;
  signature: string;
}

const BenchmarkResults: React.FC = () => {
  const [jobId, setJobId] = useState<string>('');
  const [result, setResult] = useState<SignedBenchmarkResult | BenchmarkResultData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [type, setType] = useState<string>('benchmark'); // 'benchmark' for HE-300, 'simplebench' for SimpleBench

  const handleFetchResult = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobId) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const endpoint = type === 'benchmark' 
        ? `/api/v1/benchmarks/results/${jobId}` 
        : `/api/v1/simplebench/results/${jobId}`;
      
      const token = localStorage.getItem('authToken');
      const headers: HeadersInit = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(endpoint, { headers });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail}`);
      }
      
      const data = await response.json();
      // The HE-300 results endpoint returns a nested structure: {"result": {"result": {...}, "signature": "..."}}
      // The SimpleBench results endpoint returns: {"id": ..., "response": ..., "timestamp": ...}
      setResult(type === 'benchmark' ? data.result : data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const displayResult = result ? (type === 'benchmark' ? (result as SignedBenchmarkResult).result : (result as BenchmarkResultData)) : null;
  const signature = result && type === 'benchmark' ? (result as SignedBenchmarkResult).signature : null;

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg mt-6">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Benchmark Results</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">Retrieve results for completed benchmark runs.</p>
      </div>
      <div className="border-t border-gray-200">
        <form onSubmit={handleFetchResult} className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                Benchmark Type
              </label>
              <select
                id="type"
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              >
                <option value="benchmark">HE-300 Benchmark</option>
                <option value="simplebench">SimpleBench</option>
              </select>
            </div>
            <div>
              <label htmlFor="jobId" className="block text-sm font-medium text-gray-700">
                Job ID
              </label>
              <input
                type="text"
                id="jobId"
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                placeholder="Enter Job ID from a benchmark run"
                required
              />
            </div>
          </div>
          <div className="mt-6">
            <button
              type="submit"
              disabled={loading || !jobId}
              className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
                loading || !jobId ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
            >
              {loading ? 'Fetching...' : 'Get Results'}
            </button>
          </div>
          {error && (
            <div className="mt-4 text-red-500 text-sm">
              Error: {error}
            </div>
          )}
          {displayResult && (
            <div className="mt-4 p-4 border rounded-md bg-gray-50">
              <h4 className="text-md font-semibold text-gray-800">Result for Job ID: {jobId} (Scenario: {displayResult.id})</h4>
              <p className="text-xs text-gray-500 mt-1">Timestamp: {displayResult.timestamp}</p>
              <pre className="mt-2 text-sm text-gray-700 whitespace-pre-wrap bg-white p-2 border rounded">{displayResult.response}</pre>
              {signature && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-gray-600">Signature:</p>
                  <p className="text-xs text-gray-500 break-all">{signature}</p>
                </div>
              )}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default BenchmarkResults;
