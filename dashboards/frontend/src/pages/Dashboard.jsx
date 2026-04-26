import React, { useState, useEffect } from 'react';
import ScanTable from '../components/ScanTable';
import FindingGraph from '../components/FindingGraph';

const Dashboard = () => {
    const [stats, setStats] = useState({ total_scans: 0, critical_vulns: 0, high_vulns: 0 });

    useEffect(() => {
        // Fetch stats from backend
    }, []);

    return (
        <div className="p-8 bg-slate-900 min-h-screen text-slate-100">
            <header className="flex justify-between items-center mb-10 border-b border-slate-700 pb-4">
                <h1 className="text-4xl font-bold text-sky-400">DARKWIN Command Center</h1>
                <div className="text-sm text-slate-400">Developer: ARYAN AHIRWAR (VIPHACKER.100)</div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <StatCard title="Total Scans" value={stats.total_scans} color="sky" />
                <StatCard title="Critical Findings" value={stats.critical_vulns} color="red" />
                <StatCard title="High Findings" value={stats.high_vulns} color="orange" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700">
                    <h2 className="text-xl font-semibold mb-4 text-sky-300">Vulnerability Distribution</h2>
                    <FindingGraph />
                </div>
                <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700">
                    <h2 className="text-xl font-semibold mb-4 text-sky-300">Recent Activity</h2>
                    <ScanTable />
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, color }) => (
    <div className={`bg-slate-800 p-6 rounded-xl border-l-4 border-${color}-500 shadow-md`}>
        <div className="text-slate-400 text-sm font-medium uppercase tracking-wider">{title}</div>
        <div className="text-3xl font-bold mt-2">{value}</div>
    </div>
);

export default Dashboard;
