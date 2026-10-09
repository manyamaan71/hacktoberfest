import React from 'react';
import { X, History, Trash2, ExternalLink, ArrowRight } from 'lucide-react';
import { HistoryItem } from '../types';

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: HistoryItem[];
  onSelect: (id: string) => void;
  onClear: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelect,
  onClear
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md bg-dark-surface border-l border-dark-border h-full p-6 space-y-6 flex flex-col justify-between shadow-2xl">
        <div className="space-y-6 flex-1 overflow-hidden flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-dark-border pb-4">
            <div className="flex items-center space-x-2">
              <History className="w-5 h-5 text-brand-indigo" />
              <h3 className="text-lg font-bold text-white">Investigation History</h3>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-dark-panel transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <p className="text-xs text-slate-400">
            Stored locally in your browser session. Re-select any past investigation to inspect its verified evidence report.
          </p>

          {/* List */}
          {history.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 rounded-xl bg-dark-panel border border-dashed border-dark-border">
              <History className="w-8 h-8 text-slate-600 mb-2" />
              <p className="text-xs text-slate-400">No past investigations recorded yet.</p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {history.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    onSelect(item.id);
                    onClose();
                  }}
                  className="p-3.5 rounded-xl bg-dark-card hover:bg-dark-panel border border-dark-border hover:border-brand-violet/50 transition-all cursor-pointer group space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-brand-cyan group-hover:text-white transition-colors">
                      {item.repo}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-dark-bg text-emerald-400 border border-emerald-500/30 uppercase font-bold">
                      {item.status}
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-white line-clamp-2">{item.title}</p>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1 border-t border-dark-border/40">
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                    <span className="flex items-center space-x-1 text-brand-violet group-hover:translate-x-0.5 transition-transform">
                      <span>View</span>
                      <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer actions */}
        {history.length > 0 && (
          <div className="pt-4 border-t border-dark-border flex items-center justify-between">
            <button
              onClick={onClear}
              className="px-3 py-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>

            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-dark-panel text-xs text-slate-300 font-semibold hover:text-white transition-colors"
            >
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
