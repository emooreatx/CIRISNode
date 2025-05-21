"use client";
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Scenario {
  question_id: number;
  prompt: string;
  answer: string;
}

interface SimpleBenchData {
  eval_data: Scenario[];
}

// Expected response structure from the simplebench/run endpoint
interface SimpleBenchRunResponse {
  job_id: string;
  message: string;
  results_url?: string; // Optional, based on backend implementation
}

const SimpleBenchRunner: React.FC = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenarioIds, setSelectedScenarioIds] = useState<number[]>([]);
  const [provider, setProvider] = useState('openai'); // openai or ollama
  const [apiKey, setApiKey] = useState('');
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [selectedOllamaModel, setSelectedOllamaModel] = useState('');
  
  // Define a more specific type for results
  interface BenchResult {
    scenario_id: number;
    prompt: string;
    llm_response?: string;
    expected_answer: string;
    model_used?: string;
    error?: string;
  }
  const [results, setResults] = useState<BenchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingScenarios, setLoadingScenarios] = useState(true);
  const [loadingOllamaModels, setLoadingOllamaModels] = useState(false);

  // Fetch SimpleBench scenarios
  useEffect(() => {
    const fetchScenarios = async () => {
      setLoadingScenarios(true);
      try {
        const response = await axios.get<SimpleBenchData>('/simple_bench_public.json');
        setScenarios(response.data.eval_data);
      } catch (err) {
        let message = 'Failed to load SimpleBench scenarios.';
        if (axios.isAxiosError(err)) {
          const errorData = err.response?.data as { detail?: string } | undefined;
          message += `: ${errorData?.detail || err.message}`;
          console.error("Error loading scenarios (Axios):", errorData || err.message);
        } else if (err instanceof Error) {
          message += `: ${err.message}`;
          console.error("Error loading scenarios (Generic):", err.message);
        } else {
          message += ': An unknown error occurred.';
          console.error("Error loading scenarios (Unknown):", err);
        }
        setError(message);
      } finally {
        setLoadingScenarios(false);
      }
    };
    fetchScenarios();
  }, []);

  // Fetch Ollama models when provider is Ollama
  useEffect(() => {
    if (provider === 'ollama') {
      const fetchOllamaModels = async () => {
        setLoadingOllamaModels(true);
        setError(null);
        try {
          const res = await axios.get<{ models: { name: string }[] }>("http://127.0.0.1:8001/api/v1/ollama-models");
          if (res.data.models && res.data.models.length > 0) {
            console.log("Ollama models API response:", res.data.models);
            const modelNames = res.data.models.map(m => typeof m === 'string' ? m : m.name);
            setOllamaModels(modelNames);
            console.log("Ollama models state after setting:", modelNames);
            if (modelNames.length > 0) {
              setSelectedOllamaModel(modelNames[0]);
            }
          } else {
            setOllamaModels([]);
            setSelectedOllamaModel('');
            setError('No Ollama models found. Ensure Ollama is running and accessible at the correct endpoint.');
          }
        } catch (err) {
          let errorMessage = 'Failed to fetch Ollama models';
          if (axios.isAxiosError<{ detail?: string }>(err)) {
            errorMessage += ': ' + (err.response?.data?.detail || err.message);
            console.error("Error fetching Ollama models (Axios):", {
              message: err.message,
              response: err.response?.data,
              config: err.config,
              status: err.response?.status, // Log response status
              headers: err.response?.headers, // Log response headers
              stack: err.stack, // Log the full error stack
            });
          } else if (err instanceof Error) {
            errorMessage += ': ' + err.message;
            console.error("Error fetching Ollama models (Generic):", err.message);
          } else {
            errorMessage += ': An unknown error occurred.';
            console.error("Error fetching Ollama models (Unknown):", err);
          }
          setError(errorMessage);
          setOllamaModels([]);
          setSelectedOllamaModel('');
        } finally {
          setLoadingOllamaModels(false);
        }
      };
      fetchOllamaModels();
    } else {
      setOllamaModels([]);
      setSelectedOllamaModel('');
    }
  }, [provider]);

  const handleScenarioSelection = (scenarioId: number) => {
    setSelectedScenarioIds(prevSelected =>
      prevSelected.includes(scenarioId)
        ? prevSelected.filter(id => id !== scenarioId)
        : [...prevSelected, scenarioId]
    );
  };

  const handleRunSimpleBench = async () => {
    if (selectedScenarioIds.length === 0) {
      setError('Please select at least one scenario.');
      return;
    }
    if (provider === 'openai' && !apiKey) {
      setError('Please enter an API key for OpenAI.');
      return;
    }
    if (provider === 'ollama' && !selectedOllamaModel) {
      setError('Please select an Ollama model.');
      return;
    }

    setLoading(true);
    setError(null);
    setResults([]);

    let modelToSend = '';
    if (provider === 'ollama') {
        modelToSend = selectedOllamaModel;
    } else if (provider === 'openai') {
        // apiKey is guaranteed to be present here due to the early return check
        modelToSend = 'gpt-3.5-turbo'; // Default OpenAI model, or could be made configurable
    }

    const requestBody = {
      scenario_ids: selectedScenarioIds,
      provider: provider,
      apiKey: provider === 'openai' ? apiKey : undefined,
      model: modelToSend,
    };

    try {
      // Call the updated /api/v1/simplebench/run endpoint
      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJuYW1lIjoiVGVzdCBVc2VyIiwiaWF0IjoxNjgwMDAwMDAwfQ.abc123"; // Replace with the generated JWT
      const res = await axios.post<SimpleBenchRunResponse>(
        "http://127.0.0.1:8001/api/v1/benchmarks/simplebench/run",
        requestBody,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // The backend now returns a job_id. The actual results will be fetched separately or pushed via WebSocket.
      // For now, let's display a message indicating the job has started.
      // The results display logic will need to be updated to fetch results using the job_id.
      setResults([{
        scenario_id: 0, // Placeholder, as results are not immediately available
        prompt: `SimpleBench job submitted with ID: ${res.data.job_id}. Provider: ${provider}, Model: ${requestBody.model}.`,
        llm_response: `Status: ${res.data.message}. Check results using job ID. Results URL (if available): ${res.data.results_url || 'N/A'}`,
        expected_answer: "",
        model_used: requestBody.model
      }]);
      // TODO: Implement fetching results for the job_id, or use WebSockets.
      // For now, the results area will show this submission message.
      // The actual scenario results are in a JSON file on the server, pointed to by results_url in the job status.
      // The /simplebench/results/{job_id} endpoint needs to be able to serve this.

    } catch (err) {
      let errorMessage = "An error occurred while running SimpleBench";
      if (axios.isAxiosError<{ detail?: string }>(err)) {
        errorMessage += ": " + (err.response?.data?.detail || err.message);
        console.error("Error in handleRunSimpleBench (Axios):", err.response?.data || err.message);
      } else if (err instanceof Error) {
        errorMessage += ": " + err.message;
        console.error("Error in handleRunSimpleBench (Generic):", err.message);
      } else {
        errorMessage += ": Unknown error";
        console.error("Error in handleRunSimpleBench (Unknown):", err);
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (loadingScenarios) {
    return <p>Loading SimpleBench scenarios...</p>;
  }

  return (
    <div style={{ margin: '20px auto', padding: '20px', border: '1px solid #333', borderRadius: '8px', maxWidth: '800px', backgroundColor: '#f9f9f9' }}>
      <h2 style={{ textAlign: 'center', color: '#333', marginBottom: '20px' }}>Run SimpleBench Scenarios</h2>
      
      {/* AI Provider and Model Selection */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Provider Selection</h3>
        <select
          title="Select AI Provider"
          value={provider} 
          onChange={(e) => setProvider(e.target.value)}
          style={{ padding: '8px', width: '100%', marginBottom: '10px' }}
        >
          <option value="openai">OpenAI</option>
          <option value="ollama">Ollama</option>
        </select>

        {provider === 'openai' && (
          <div>
            <h3>OpenAI API Key</h3>
            <input 
              type="password" 
              value={apiKey} 
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your OpenAI API key" 
              style={{ padding: '8px', width: '100%' }}
            />
          </div>
        )}

        {provider === 'ollama' && (
          <div>
            <h3>Ollama Model Selection</h3>
            {loadingOllamaModels ? (
              <p>Loading Ollama models...</p>
            ) : (
              <select
                title="Select Ollama Model"
                value={selectedOllamaModel} 
                onChange={(e) => setSelectedOllamaModel(e.target.value)}
                style={{ padding: '8px', width: '100%' }}
                disabled={ollamaModels.length === 0}
              >
                {ollamaModels.length > 0 ? (
                  ollamaModels.map((model, index) => (
                    <option key={index} value={model}>{model}</option>
                  ))
                ) : (
                  <option value="">No models available</option>
                )}
              </select>
            )}
          </div>
        )}
      </div>

      {/* Scenario Selection */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Scenarios</h3>
        <div style={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px' }}>
          {scenarios.map((scenario) => (
            <div key={scenario.question_id} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #eee', borderRadius: '4px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                <input 
                  type="checkbox" 
                  checked={selectedScenarioIds.includes(scenario.question_id)} 
                  onChange={() => handleScenarioSelection(scenario.question_id)} 
                  style={{ marginRight: '10px' }}
                />
                Scenario {scenario.question_id}
              </label>
              <div style={{ marginLeft: '25px' }}>
                <strong>Prompt:</strong> <p>{scenario.prompt}</p>
                <strong>Expected Answer:</strong> <p>{scenario.answer}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Run Button */}
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <button 
          onClick={handleRunSimpleBench} 
          disabled={loading || selectedScenarioIds.length === 0}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#cccccc' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Running SimpleBench...' : 'Run Selected Scenarios'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{ color: 'red', marginBottom: '20px', padding: '10px', border: '1px solid red', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      {/* Results Display */}
      {results.length > 0 && (
        <div>
          <h3>Results</h3>
          <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px' }}>
            {results.map((result, index) => (
              <div key={index} style={{ marginBottom: '20px', padding: '15px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f5f5f5' }}>
                <p><strong>Scenario ID:</strong> {result.scenario_id}</p>
                <p><strong>Prompt:</strong> {result.prompt}</p>
                <p><strong>Model Used:</strong> {result.model_used}</p>
                <div><strong>LLM Response:</strong> <pre style={{ whiteSpace: 'pre-wrap', backgroundColor: '#eef', padding: '10px', borderRadius: '4px' }}>{result.llm_response}</pre></div>
                <div><strong>Expected Answer:</strong> <pre style={{ whiteSpace: 'pre-wrap', backgroundColor: '#efe', padding: '10px', borderRadius: '4px' }}>{result.expected_answer}</pre></div>
                {result.error && <p style={{ color: 'red' }}><strong>Error:</strong> {result.error}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleBenchRunner;
