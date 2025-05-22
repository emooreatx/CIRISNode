"use client";
import React, { useEffect, useState } from "react";

const BenchmarkContentViewer: React.FC = () => {
  interface Scenario {
    id: string;
    prompt: string;
  }

  const [he300Content, setHe300Content] = useState<Scenario[]>([]);
  const [simpleBenchContent, setSimpleBenchContent] = useState<Scenario[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const he300Response = await fetch("/api/v1/benchmarks/content/he300");
        if (!he300Response.ok) {
          throw new Error("Failed to fetch HE-300 content");
        }
        const he300Data = await he300Response.json();
        setHe300Content(he300Data);

        const simpleBenchResponse = await fetch(
          "/api/v1/benchmarks/content/simplebench"
        );
        if (!simpleBenchResponse.ok) {
          throw new Error("Failed to fetch SimpleBench content");
        }
        const simpleBenchData = await simpleBenchResponse.json();
        setSimpleBenchContent(simpleBenchData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred");
      }
    };

    fetchContent();
  }, []);

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg mt-6">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Benchmark Content Viewer
        </h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">
          View and select specific scenarios for HE-300 and SimpleBench.
        </p>
      </div>
      <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
        {error && (
          <div className="text-red-500 text-sm mb-4">Error: {error}</div>
        )}
        <div>
          <h4 className="text-md font-medium text-gray-900">HE-300 Scenarios</h4>
          <ul className="list-disc pl-5 mt-2">
            {he300Content.map((scenario, index) => (
              <li key={index} className="text-gray-700">
                {scenario.prompt}
              </li>
            ))}
          </ul>
        </div>
        <div className="mt-6">
          <h4 className="text-md font-medium text-gray-900">
            SimpleBench Scenarios
          </h4>
          <ul className="list-disc pl-5 mt-2">
            {simpleBenchContent.map((scenario, index) => (
              <li key={index} className="text-gray-700">
                {scenario.prompt}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default BenchmarkContentViewer;
