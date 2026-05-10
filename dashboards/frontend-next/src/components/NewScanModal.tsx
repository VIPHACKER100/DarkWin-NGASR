"use client";

import React, { useState } from 'react';
import { X, Zap, Shield, Globe, Terminal } from 'lucide-react';

interface NewScanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStart: (target: string, pipeline: string) => void;
  isScanning: boolean;
}

export default function NewScanModal({ isOpen, onClose, onStart, isScanning }: NewScanModalProps) {
  const [target, setTarget] = useState('');
  const [pipeline, setPipeline] = useState('recon');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-md bg-zinc-950 border border-white/10 rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="h-2 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600" />
        
        <div className="p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-cyan-500/10 rounded-xl flex items-center justify-center border border-cyan-500/20">
                <Zap size={20} className="text-cyan-400" />
              </div>
              <h3 className="text-xl font-bold">Initiate Research</h3>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-white/5 rounded-full transition-colors text-zinc-500 hover:text-white"
            >
              <X size={20} />
            </button>
          </div>

          <div className="space-y-6">
            {/* Target Input */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                <Globe size={12} /> Target Scope
              </label>
              <div className="relative">
                <input 
                  type="text" 
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="example.com or 192.168.1.1"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-cyan-500/50 transition-colors pl-10"
                />
                <Globe size={18} className="absolute left-3 top-3 text-zinc-600" />
              </div>
            </div>

            {/* Pipeline Selection */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                <Terminal size={12} /> Pipeline Strategy
              </label>
              <div className="grid grid-cols-3 gap-3">
                <PipelineOption 
                  id="recon" 
                  label="Recon" 
                  active={pipeline === 'recon'} 
                  onClick={() => setPipeline('recon')} 
                  icon={<Shield size={16} />}
                />
                <PipelineOption 
                  id="scan" 
                  label="Scan" 
                  active={pipeline === 'scan'} 
                  onClick={() => setPipeline('scan')} 
                  icon={<Zap size={16} />}
                />
                <PipelineOption 
                  id="hunt" 
                  label="Hunt" 
                  active={pipeline === 'hunt'} 
                  onClick={() => setPipeline('hunt')} 
                  icon={<Activity size={16} />}
                />
              </div>
            </div>

            <div className="p-4 bg-cyan-500/5 border border-cyan-500/10 rounded-2xl">
              <p className="text-[11px] text-zinc-400 leading-relaxed italic">
                {pipeline === 'recon' && "Deep reconnaissance including subdomain discovery and port mapping."}
                {pipeline === 'scan' && "Standard vulnerability assessment against identified services."}
                {pipeline === 'hunt' && "Aggressive AI-driven autonomous hunting for critical vulnerabilities."}
              </p>
            </div>

            <button 
              onClick={() => onStart(target, pipeline)}
              disabled={!target || isScanning}
              className="w-full btn-primary py-4 flex items-center justify-center gap-3 disabled:opacity-50 disabled:grayscale transition-all"
            >
              <Zap size={20} className={isScanning ? "animate-spin" : ""} />
              <span className="font-bold tracking-tight">
                {isScanning ? "Engaging Pipeline..." : "Engage Research"}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function PipelineOption({ id, label, active, onClick, icon }: any) {
  return (
    <button 
      onClick={onClick}
      className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all ${
        active 
          ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' 
          : 'bg-white/5 border-white/5 text-zinc-500 hover:border-white/10'
      }`}
    >
      {icon}
      <span className="text-[10px] font-bold uppercase">{label}</span>
    </button>
  );
}

function Activity({ size, className }: any) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      className={className}
    >
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}
