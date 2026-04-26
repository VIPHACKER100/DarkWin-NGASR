import React from 'react';

const ScanTable = () => {
    const mockScans = [
        { id: 'DW-101', target: 'example.com', status: 'Completed', date: '2026-04-26' },
        { id: 'DW-102', target: 'api.test.org', status: 'Running', date: '2026-04-26' },
        { id: 'DW-103', target: 'staging.app.io', status: 'Failed', date: '2026-04-25' },
    ];

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left">
                <thead>
                    <tr className="text-slate-400 border-b border-slate-700">
                        <th className="py-3 px-2">ID</th>
                        <th className="py-3 px-2">Target</th>
                        <th className="py-3 px-2">Status</th>
                        <th className="py-3 px-2">Date</th>
                    </tr>
                </thead>
                <tbody>
                    {mockScans.map((scan) => (
                        <tr key={scan.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                            <td className="py-4 px-2 font-mono text-sky-400">{scan.id}</td>
                            <td className="py-4 px-2">{scan.target}</td>
                            <td className="py-4 px-2">
                                <span className={`px-2 py-1 rounded text-xs font-bold ${
                                    scan.status === 'Completed' ? 'bg-green-500/20 text-green-400' :
                                    scan.status === 'Running' ? 'bg-sky-500/20 text-sky-400' : 'bg-red-500/20 text-red-400'
                                }`}>
                                    {scan.status}
                                </span>
                            </td>
                            <td className="py-4 px-2 text-slate-500">{scan.date}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default ScanTable;
