import React from 'react';
import { Search, History, HelpCircle, Settings, PlusCircle, ChevronRight } from 'lucide-react';
import { HistoryItem } from '../types';

interface SidebarProps {
  currentView: 'home' | 'workspace';
  onNewInvestigation: () => void;
  onOpenHistory: () => void;
  onOpenHowItWorks: () => void;
  onOpenModelModal: () => void;
  history: HistoryItem[];
  onSelectHistoryItem: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onNewInvestigation,
  onOpenHistory,
  onOpenHowItWorks,
  onOpenModelModal,
  history,
  onSelectHistoryItem
}) => {
  return (
    <aside className="w-64 bg-dark-surface border-r border-dark-border min-h-[calc(100vh-65px)] p-4 hidden lg:flex flex-col justify-between">
      <div className="space-y-6">
        {/* Primary Action Button */}
        <button
          onClick={onNewInvestigation}
          className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-brand-violet to-brand-indigo hover:from-brand-indigo hover:to-brand-violet text-white font-semibold text-sm shadow-glow-violet transition-all transform hover:-translate-y-0.5 active:translate-y-0"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Investigation</span>
        </button>

        {/* Navigation Items */}
        <nav className="space-y-1">
          <button
            onClick={onNewInvestigation}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              currentView === 'home'
                ? 'bg-brand-violet/15 text-brand-violet border border-brand-violet/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-dark-panel'
            }`}
          >
            <div className="flex items-center space-x-2.5">
              <Search className="w-4 h-4" />
              <span>Dashboard</span>
            </div>
            {currentView === 'home' && <ChevronRight className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={onOpenHistory}
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-dark-panel transition-colors"
          >
            <div className="flex items-center space-x-2.5">
              <History className="w-4 h-4 text-brand-indigo" />
              <span>Investigation History</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-dark-border text-slate-400">{history.length}</span>
          </button>

          <button
            onClick={onOpenHowItWorks}
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-dark-panel transition-colors"
          >
            <div className="flex items-center space-x-2.5">
              <HelpCircle className="w-4 h-4 text-brand-cyan" />
              <span>How It Works</span>
            </div>
          </button>

          <button
            onClick={onOpenModelModal}
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-dark-panel transition-colors"
          >
            <div className="flex items-center space-x-2.5">
              <Settings className="w-4 h-4 text-slate-400" />
              <span>Model Settings</span>
            </div>
          </button>
        </nav>

        {/* Local History Section */}
        <div className="pt-4 border-t border-dark-border">
          <div className="flex items-center justify-between px-2 mb-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Recent Investigations</span>
            <span className="text-[9px] text-slate-500">Local storage</span>
          </div>

          {history.length === 0 ? (
            <div className="px-2 py-3 text-center rounded-lg bg-dark-panel border border-dashed border-dark-border">
              <p className="text-xs text-slate-500">No past investigations yet.</p>
            </div>
          ) : (
            <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
              {history.slice(0, 5).map((item) => (
                <button
                  key={item.id}
                  onClick={() => onSelectHistoryItem(item.id)}
                  className="w-full text-left p-2 rounded-lg bg-dark-panel hover:bg-dark-card border border-dark-border hover:border-slate-600 transition-colors group"
                >
                  <p className="text-xs font-semibold text-slate-300 group-hover:text-brand-cyan truncate">
                    {item.repo} #{item.title}
                  </p>
                  <p className="text-[10px] text-slate-500 truncate mt-0.5">
                    {new Date(item.timestamp).toLocaleDateString()}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer info */}
      <div className="pt-4 border-t border-dark-border text-center">
        <p className="text-[11px] text-slate-500">
          RepoXray v1.0.0 — Open Source
        </p>
      </div>
    </aside>
  );
};
