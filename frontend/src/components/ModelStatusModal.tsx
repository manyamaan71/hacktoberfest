import React from 'react';
import { X, Cpu, CheckCircle2, AlertTriangle, RefreshCw, Key, ShieldCheck } from 'lucide-react';
import { ModelStatusResponse } from '../types';

interface ModelStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  status: ModelStatusResponse | null;
  onRefresh: () => void;
}

export const ModelStatusModal: React.FC<ModelStatusModalProps> = ({
  isOpen,
  onClose,
  status,
  onRefresh
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-lg p-6 rounded-2xl border border-dark-border shadow-2xl space-y-5 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-dark-panel transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-brand-violet/20 text-brand-violet flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Gemma 4 Model Provider</h3>
            <p className="text-xs text-slate-400">Backend AI Agent configuration check</p>
          </div>
        </div>

        {/* Status Card */}
        <div className="p-4 rounded-xl bg-dark-card border border-dark-border space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium">Provider:</span>
            <span className="font-mono font-semibold text-white uppercase">{status?.provider || 'Google'}</span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium">Model ID:</span>
            <span className="font-mono font-semibold text-brand-cyan">{status?.model || 'gemma-4b'}</span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium">Status:</span>
            {status?.configured ? (
              <span className="flex items-center space-x-1 font-semibold text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{status.status === 'connectivity_verified' ? 'Verified Online' : 'Configured'}</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 font-semibold text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Unconfigured (Heuristic Mode)</span>
              </span>
            )}
          </div>
        </div>

        {/* Message */}
        <div className="p-3 rounded-lg bg-dark-bg border border-dark-border text-xs text-slate-300 leading-relaxed font-sans">
          {status?.message || 'Checking model endpoint...'}
        </div>

        {/* Instructions */}
        <div className="space-y-2 text-xs text-slate-400 border-t border-dark-border/60 pt-4">
          <h4 className="font-bold text-white flex items-center space-x-1.5">
            <Key className="w-3.5 h-3.5 text-brand-violet" />
            <span>How to configure Gemma API credentials:</span>
          </h4>
          <ol className="list-decimal list-inside space-y-1 font-mono text-[11px] text-slate-300">
            <li>Open <code className="text-brand-cyan">backend/.env</code> in your workspace.</li>
            <li>Set <code className="text-emerald-400">GEMMA_API_KEY=your_gemini_api_key</code>.</li>
            <li>Restart the backend server (`uvicorn app.main:app`).</li>
          </ol>
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={onRefresh}
            className="px-4 py-2 rounded-lg bg-dark-surface hover:bg-dark-panel border border-dark-border text-xs font-semibold text-slate-200 flex items-center space-x-2 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Re-check Connectivity</span>
          </button>

          <button
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-brand-violet hover:bg-brand-indigo text-xs font-semibold text-white transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
