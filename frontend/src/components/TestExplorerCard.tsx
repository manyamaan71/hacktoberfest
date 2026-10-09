import React from 'react';
import { TestTube2, ExternalLink, ShieldCheck, Binary } from 'lucide-react';
import { CandidateTest } from '../types';

interface TestExplorerCardProps {
  tests: CandidateTest[];
}

export const TestExplorerCard: React.FC<TestExplorerCardProps> = ({ tests }) => {
  return (
    <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-4">
      <div className="flex items-center justify-between border-b border-dark-border/60 pb-3">
        <div className="flex items-center space-x-2">
          <TestTube2 className="w-5 h-5 text-brand-cyan" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Candidate Test Suite</h3>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-dark-panel text-slate-400 border border-dark-border">
          {tests.length} test file{tests.length !== 1 ? 's' : ''}
        </span>
      </div>

      {tests.length === 0 ? (
        <div className="p-4 rounded-xl bg-dark-card border border-dark-border text-center">
          <p className="text-xs text-slate-400">No test files matching issue terms were found in candidate search.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tests.map((test, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-dark-card border border-dark-border hover:border-slate-600 transition-colors space-y-2.5"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2 font-mono text-xs font-semibold text-slate-200">
                  <TestTube2 className="w-4 h-4 text-brand-cyan" />
                  <span className="text-white">{test.path}</span>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/30">
                    {test.match_type.replace('_', ' ')}
                  </span>
                  {test.url && (
                    <a
                      href={test.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 rounded hover:bg-dark-panel text-slate-400 hover:text-white transition-colors"
                      title="View test on GitHub"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>

              {test.test_functions.length > 0 && (
                <div className="flex flex-wrap gap-1.5 text-[11px] font-mono">
                  {test.test_functions.map((fn, fIdx) => (
                    <span key={fIdx} className="px-2 py-0.5 rounded bg-dark-bg text-emerald-400 border border-emerald-500/20">
                      {fn}
                    </span>
                  ))}
                </div>
              )}

              <p className="text-xs text-slate-300 font-sans">{test.reason}</p>

              {test.excerpt && (
                <div className="p-3 rounded-lg bg-[#080B10] border border-dark-border text-slate-300 font-mono text-xs overflow-x-auto">
                  <pre className="whitespace-pre">{test.excerpt}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
