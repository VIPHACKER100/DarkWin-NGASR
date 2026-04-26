import React from 'react';

const ConfigPanel = () => {
    return (
        <div className="p-6 bg-slate-800 rounded-xl border border-slate-700">
            <h2 className="text-2xl font-bold mb-6 text-sky-400">Platform Settings</h2>
            
            <div className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Shodan API Key</label>
                    <input type="password" placeholder="••••••••••••••••" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-slate-100 focus:ring-2 focus:ring-sky-500 outline-none" />
                </div>
                
                <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Max Threads</label>
                    <input type="number" defaultValue="20" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-slate-100 focus:ring-2 focus:ring-sky-500 outline-none" />
                </div>
                
                <button className="bg-sky-600 hover:bg-sky-500 text-white font-bold py-3 px-8 rounded-lg transition-colors shadow-lg">
                    Save Configuration
                </button>
            </div>
        </div>
    );
};

export default ConfigPanel;
