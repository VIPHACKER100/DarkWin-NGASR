import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { Shield, Activity, Target, Database, FileText } from 'lucide-react';

function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-darkwin-accent mb-6">DARKWIN Command Center</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-darkwin-card p-4 rounded-lg border border-gray-800 shadow-lg">
          <h3 className="text-gray-400">Active Targets</h3>
          <p className="text-2xl font-bold mt-2 text-darkwin-accent">12</p>
        </div>
        <div className="bg-darkwin-card p-4 rounded-lg border border-gray-800 shadow-lg">
          <h3 className="text-gray-400">Running Scans</h3>
          <p className="text-2xl font-bold mt-2 text-darkwin-warning">3</p>
        </div>
        <div className="bg-darkwin-card p-4 rounded-lg border border-gray-800 shadow-lg">
          <h3 className="text-gray-400">Critical Findings</h3>
          <p className="text-2xl font-bold mt-2 text-darkwin-danger">5</p>
        </div>
        <div className="bg-darkwin-card p-4 rounded-lg border border-gray-800 shadow-lg">
          <h3 className="text-gray-400">Total Findings</h3>
          <p className="text-2xl font-bold mt-2 text-darkwin-success">142</p>
        </div>
      </div>
      <div className="mt-8">
        <h2 className="text-xl font-bold text-white mb-4">Developed by ARYAN AHIRWAR (VIPHACKER.100)</h2>
        <p className="text-gray-400">The Next-Generation Automated Security Research Platform.</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div className="flex h-screen bg-darkwin-dark text-white">
      {/* Sidebar */}
      <div className="w-64 bg-darkwin-card border-r border-gray-800">
        <div className="p-4 border-b border-gray-800 flex items-center gap-2">
          <Shield className="text-darkwin-accent" />
          <span className="text-xl font-bold tracking-wider">DARKWIN</span>
        </div>
        <nav className="p-4 flex flex-col gap-2">
          <Link to="/" className="flex items-center gap-3 p-2 hover:bg-gray-800 rounded text-gray-300 hover:text-white transition-colors">
            <Activity size={18} /> Dashboard
          </Link>
          <Link to="/targets" className="flex items-center gap-3 p-2 hover:bg-gray-800 rounded text-gray-300 hover:text-white transition-colors">
            <Target size={18} /> Targets
          </Link>
          <Link to="/findings" className="flex items-center gap-3 p-2 hover:bg-gray-800 rounded text-gray-300 hover:text-white transition-colors">
            <Database size={18} /> Findings
          </Link>
          <Link to="/reports" className="flex items-center gap-3 p-2 hover:bg-gray-800 rounded text-gray-300 hover:text-white transition-colors">
            <FileText size={18} /> Reports
          </Link>
        </nav>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/targets" element={<div className="p-6 text-xl">Targets Module (Coming Soon)</div>} />
          <Route path="/findings" element={<div className="p-6 text-xl">Findings Module (Coming Soon)</div>} />
          <Route path="/reports" element={<div className="p-6 text-xl">Reports Module (Coming Soon)</div>} />
        </Routes>
      </div>
    </div>
  );
}
