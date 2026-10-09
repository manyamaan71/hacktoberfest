import React from 'react';
import { Search, Activity, Cpu, HelpCircle, History, ExternalLink, ShieldCheck, AlertTriangle } from 'lucide-react';
import { ModelStatusResponse } from '../types';

interface NavbarProps {
  modelStatus: ModelStatusResponse | null;
  onOpenModelModal: () => void;
  onOpenHowItWorks: () => void;
  onOpenHistory: () => void;
  onNewInvestigation: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  modelStatus,
  onOpenModelModal,
  onOpenHowItWorks,
  onOpenHistory,
  onNewInvestigation
}) => {
  return (
    <header className="sticky top-0 z-40 bg-[#0A0D14]/90 backdrop-blur-md border-b border-dark-border px-4 lg:px-6 py-3 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Header */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={onNewInvestigation}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-violet via-brand-indigo to-brand-cyan p-0.5 shadow-glow-violet flex items-center justify-center">
            <div className="w-full h-full bg-dark-bg rounded-[10px] flex items-center justify-center">
              <Search className="w-5 h-5 text-brand-cyan" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400 font-mono">
                REPO<span className="text-brand-cyan">XRAY</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase bg-brand-violet/20 text-brand-violet rounded-full border border-brand-violet/30">
                AI Agent
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium hidden sm:block">
              Investigate smarter. Contribute confidently.
            </p>
          </div>
        </div>

        {/* Right Navigation & Status Indicators */}
        <div className="flex items-center space-x-3">
          {/* Model Connection Status Indicator */}
          <button
            onClick={onOpenModelModal}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-dark-surface border border-dark-border hover:border-slate-600 transition-colors"
            title="Configure Gemma Model Settings"
          >
            <Cpu className="w-3.5 h-3.5 text-brand-violet" />
            <span className="text-slate-300 hidden md:inline">Gemma 4:</span>
            {modelStatus?.configured ? (
              <span className="flex items-center text-emerald-400 font-semibold space-x-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>{modelStatus.status === 'connectivity_verified' ? 'Verified' : 'Configured'}</span>
              </span>
            ) : (
              <span className="flex items-center text-amber-400 font-semibold space-x-1">
                <AlertTriangle className="w-3 h-3 text-amber-400" />
                <span>Heuristic Mode</span>
              </span>
            )}
          </button>

          {/* Quick Buttons */}
          <button
            onClick={onOpenHistory}
            className="p-2 rounded-lg bg-dark-surface border border-dark-border text-slate-300 hover:text-white hover:border-slate-600 transition-colors flex items-center space-x-1.5 text-xs font-medium"
            title="Investigation History"
          >
            <History className="w-4 h-4 text-brand-indigo" />
            <span className="hidden sm:inline">History</span>
          </button>

          <button
            onClick={onOpenHowItWorks}
            className="p-2 rounded-lg bg-dark-surface border border-dark-border text-slate-300 hover:text-white hover:border-slate-600 transition-colors flex items-center space-x-1.5 text-xs font-medium"
            title="How RepoXray Works"
          >
            <HelpCircle className="w-4 h-4 text-brand-cyan" />
            <span className="hidden sm:inline">How it Works</span>
          </button>
        </div>
      </div>
    </header>
  );
};
