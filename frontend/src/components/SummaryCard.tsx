import React from 'react';
import { Sparkles, HelpCircle } from 'lucide-react';

interface SummaryCardProps {
  summary: string;
  uncertainties: string[];
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ summary, uncertainties }) => {
  return (
    <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-4">
      <div className="flex items-center space-x-2 border-b border-dark-border/60 pb-3">
        <Sparkles className="w-5 h-5 text-brand-cyan" />
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Agent Executive Summary</h3>
      </div>

      <p className="text-sm text-slate-200 leading-relaxed font-sans">{summary}</p>

      {uncertainties.length > 0 && (
        <div className="pt-2 border-t border-dark-border/40 space-y-2">
          <div className="flex items-center space-x-1.5 text-amber-400 text-xs font-semibold">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Important Uncertainties & Limitations</span>
          </div>
          <ul className="list-disc list-inside space-y-1 text-xs text-slate-400 pl-1">
            {uncertainties.map((u, i) => (
              <li key={i}>{u}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
