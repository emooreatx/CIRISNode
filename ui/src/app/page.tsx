import React from 'react';
import HealthStatus from '../components/HealthStatus';
import APIKeyManager from '../components/APIKeyManager';
import BenchmarkRunner from '../components/BenchmarkRunner';
import SimpleBenchRunner from '../components/SimpleBenchRunner';
import BenchmarkResults from '../components/BenchmarkResults';
import WBDTasks from '../components/WBDTasks';
import AuditLogs from '../components/AuditLogs';
import AgentEvents from '../components/AgentEvents';
import TestConnection from '../components/TestConnection';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">CIRISNode Dashboard</h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0 space-y-8">
            <TestConnection />
            <HealthStatus />
            <APIKeyManager />
            <BenchmarkRunner />
            <SimpleBenchRunner />
            <BenchmarkResults />
            <WBDTasks />
            <AuditLogs />
            <AgentEvents />
          </div>
        </div>
      </main>
    </div>
  );
}
