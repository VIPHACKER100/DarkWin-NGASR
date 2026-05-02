"use client";

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Shield, 
  Target as TargetIcon, 
  Zap, 
  Search, 
  AlertTriangle, 
  Download,
  Settings,
  Terminal,
  LayoutDashboard,
  BarChart3,
  FileText
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { io } from 'socket.io-client';
import AttackSurfaceGraph from '@/components/AttackSurfaceGraph';
import { fetchScans, Scan, Finding } from '@/lib/api';

// ... existing code ...

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    // API Data Loading
    async function loadData() {
      const data = await fetchScans();
      setScans(data);
      setLoading(false);
    }
    loadData();

    // WebSocket Connection
    const socket = io(process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:5000');
    
    socket.on('connect', () => {
      setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), level: 'SUCCESS', msg: 'WebSocket Connected', color: 'text-green-400' }]);
    });

    socket.on('log_event', (data) => {
      setLogs(prev => [data, ...prev].slice(0, 50)); // Keep last 50 logs
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-zinc-950 border-r border-white/5 flex flex-col p-6 gap-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-cyan-500 rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.5)]">
            <Shield size={24} className="text-black" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight">DARKWIN</h1>
            <p className="text-[10px] text-zinc-500 tracking-widest uppercase">Research v1.0</p>
          </div>
        </div>

        <nav className="flex flex-col gap-2">
          <SidebarItem 
            icon={<LayoutDashboard size={20} />} 
            label="Overview" 
            active={activeTab === 'overview'} 
            onClick={() => setActiveTab('overview')} 
          />
          <SidebarItem 
            icon={<TargetIcon size={20} />} 
            label="Targets" 
            active={activeTab === 'targets'} 
            onClick={() => setActiveTab('targets')} 
          />
          <SidebarItem 
            icon={<Zap size={20} />} 
            label="Neural Map" 
            active={activeTab === 'map'} 
            onClick={() => setActiveTab('map')} 
          />
          <SidebarItem 
            icon={<Activity size={20} />} 
            label="Live Scans" 
            active={activeTab === 'scans'} 
            onClick={() => setActiveTab('scans')} 
          />
          <SidebarItem 
            icon={<AlertTriangle size={20} />} 
            label="Findings" 
            active={activeTab === 'findings'} 
            onClick={() => setActiveTab('findings')} 
          />
          <SidebarItem 
            icon={<FileText size={20} />} 
            label="Reports" 
            active={activeTab === 'reports'} 
            onClick={() => setActiveTab('reports')} 
          />
        </nav>

        <div className="mt-auto flex flex-col gap-2">
          <SidebarItem icon={<Settings size={20} />} label="Settings" />
          <div className="p-4 glass mt-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs font-medium text-zinc-400">System Ready</span>
            </div>
            <p className="text-[10px] text-zinc-600">Local Engine: Active</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-y-auto custom-scrollbar">
        {/* Header */}
        <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-black/50 backdrop-blur-xl sticky top-0 z-10">
          <div>
            <h2 className="text-xl font-bold">Security Dashboard</h2>
            <p className="text-xs text-zinc-500">Real-time automated vulnerability monitoring</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-white/5 px-4 py-2 rounded-full border border-white/10">
              <Search size={16} className="text-zinc-500" />
              <input 
                type="text" 
                placeholder="Search targets or findings..." 
                className="bg-transparent border-none text-sm outline-none w-64"
              />
            </div>
            <button className="btn-primary flex items-center gap-2">
              <Zap size={18} />
              New Scan
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-8 flex flex-col gap-8 h-full">
          {activeTab === 'map' ? (
            <div className="h-[calc(100vh-200px)]">
              <AttackSurfaceGraph />
            </div>
          ) : activeTab === 'overview' ? (
            <>
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard label="Total Targets" value={scans.length.toString()} icon={<TargetIcon className="text-cyan-400" />} trend="+12%" />
                <StatCard label="Critical Findings" value="42" icon={<AlertTriangle className="text-red-500" />} trend="+5" trendDown={false} />
                <StatCard label="Active Scans" value={scans.filter(s => s.status === 'running').length.toString()} icon={<Activity className="text-green-400" />} trend="Live" />
                <StatCard label="System Load" value="24%" icon={<BarChart3 className="text-purple-400" />} trend="Stable" />
              </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 glass p-6 h-[400px] flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold flex items-center gap-2">
                  <Activity size={18} className="text-cyan-400" />
                  Scan Intensity & Finding Trends
                </h3>
                <select className="bg-white/5 border border-white/10 text-xs rounded-md px-2 py-1 outline-none">
                  <option>Last 24 Hours</option>
                  <option>Last 7 Days</option>
                </select>
              </div>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={scanData}>
                    <defs>
                      <linearGradient id="colorIntensity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                    <XAxis dataKey="name" stroke="#666" fontSize={10} axisLine={false} tickLine={false} />
                    <YAxis stroke="#666" fontSize={10} axisLine={false} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="intensity" 
                      stroke="#06b6d4" 
                      fillOpacity={1} 
                      fill="url(#colorIntensity)" 
                      strokeWidth={3}
                    />
                    <Line type="monotone" dataKey="findings" stroke="#ef4444" strokeWidth={2} dot={{ r: 4, fill: '#ef4444' }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass p-6 flex flex-col">
              <h3 className="font-bold mb-4 flex items-center gap-2">
                <Terminal size={18} className="text-green-400" />
                Live Execution Logs
              </h3>
              <div className="flex-1 bg-black/50 rounded-xl p-4 font-mono text-[11px] overflow-y-auto space-y-2 border border-white/5 h-[300px]">
                {logs.length === 0 ? (
                  <p className="text-zinc-600 italic">Waiting for logs...</p>
                ) : (
                  logs.map((log, i) => (
                    <LogEntry 
                      key={i}
                      time={log.time}
                      level={log.level}
                      msg={log.msg}
                      color={log.color}
                    />
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Recent Scans Table */}
          <div className="glass overflow-hidden">
            <div className="p-6 border-b border-white/5 flex items-center justify-between">
              <h3 className="font-bold uppercase tracking-wider text-sm">Recent Activity</h3>
              <button className="text-xs text-cyan-400 hover:underline">View All Scans</button>
            </div>
            {loading ? (
              <div className="p-12 text-center text-zinc-500">Loading scans...</div>
            ) : scans.length === 0 ? (
              <div className="p-12 text-center text-zinc-500">No scans found. Start one to see results!</div>
            ) : (
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-zinc-500 uppercase text-[10px] font-bold">
                  <tr>
                    <th className="px-6 py-4">Target</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Started At</th>
                    <th className="px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {scans.map((scan) => (
                    <ScanRow 
                      key={scan.id}
                      target={scan.target}
                      status={scan.status}
                      startedAt={new Date(scan.started_at).toLocaleString()}
                    />
                  ))}
                </tbody>
              </table>
            )}
          </div>
          </>
          ) : (
            <div className="flex items-center justify-center h-full text-zinc-600">
              Select a tab to view content
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function SidebarItem({ icon, label, active = false, onClick = () => {} }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
        active 
          ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' 
          : 'text-zinc-500 hover:text-white hover:bg-white/5'
      }`}
    >
      {icon}
      <span className="font-medium text-sm">{label}</span>
    </button>
  );
}

function StatCard({ label, value, icon, trend, trendDown = false }) {
  return (
    <div className="glass p-6 flex flex-col gap-4 group hover:border-cyan-500/30 transition-all">
      <div className="flex items-center justify-between">
        <div className="p-3 bg-white/5 rounded-lg group-hover:scale-110 transition-transform">
          {icon}
        </div>
        <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${
          trend === 'Live' ? 'bg-green-500/20 text-green-400 animate-pulse' :
          trendDown ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
        }`}>
          {trend}
        </span>
      </div>
      <div>
        <p className="text-zinc-500 text-xs font-medium">{label}</p>
        <h4 className="text-3xl font-bold mt-1 tracking-tight">{value}</h4>
      </div>
    </div>
  );
}

function LogEntry({ time, level, msg, color = "text-zinc-400" }) {
  const levelColor = {
    INFO: "text-blue-400",
    SUCCESS: "text-green-400",
    WARN: "text-yellow-400",
    CRITICAL: "text-red-500",
  }[level];

  return (
    <div className="flex gap-3">
      <span className="text-zinc-600 flex-shrink-0">{time}</span>
      <span className={`font-bold flex-shrink-0 w-12 ${levelColor}`}>{level}</span>
      <span className={color}>{msg}</span>
    </div>
  );
}

function ScanRow({ target, status, startedAt, verified = false }) {
  const statusColor = {
    completed: "text-green-500 bg-green-500/10 border-green-500/20",
    running: "text-cyan-500 bg-cyan-500/10 border-cyan-500/20 animate-pulse",
    failed: "text-red-500 bg-red-500/10 border-red-500/20",
    pending: "text-yellow-500 bg-yellow-500/10 border-yellow-500/20",
  }[status];

  return (
    <tr className="hover:bg-white/[0.02] transition-colors">
      <td className="px-6 py-4 font-bold flex items-center gap-2">
        {target}
        {verified && <span className="px-1.5 py-0.5 bg-green-500/10 text-green-500 text-[8px] font-bold uppercase rounded border border-green-500/20">Verified</span>}
      </td>
      <td className="px-6 py-4">
        <span className={`text-[10px] uppercase font-bold px-3 py-1 rounded-full border ${statusColor}`}>
          {status}
        </span>
      </td>
      <td className="px-6 py-4 font-mono text-[10px] text-zinc-400">{startedAt}</td>
      <td className="px-6 py-4">
        <button className="p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
          <Download size={14} />
        </button>
      </td>
    </tr>
  );
}
