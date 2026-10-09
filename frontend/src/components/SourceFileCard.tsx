import React from 'react';
import { FileCode, ExternalLink, ShieldCheck, Sparkles, Binary, Code2 } from 'lucide-react';
import { CandidateFile, EvidenceCategory } from '../types';

interface SourceFileCardProps {
  files: CandidateFile[];
}

export const SourceFileCard: React.FC<SourceFileCardProps> = ({ files }) => {
  const getBadge = (type: EvidenceCategory) => {
    switch (type) {
      case 'VERIFIED_FACT':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <ShieldCheck className="w-3 h-3" />
            <span>VERIFIED FACT</span>
          </span>
        );
      case 'AI_INFERENCE':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-brand-violet/10 text-brand-violet border border-brand-violet/30">
            <Sparkles className="w-3 h-3" />
            <span>AI INFERENCE</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/30">
            <Binary className="w-3 h-3" />
            <span>HEURISTIC MATCH</span>
          </span>
        );
    }
  };

  return (
    <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-4">
      <div className="flex items-center justify-between border-b border-dark-border/60 pb-3">
        <div className="flex items-center space-x-2">
          <FileCode className="w-5 h-5 text-brand-indigo" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Candidate Source Files</h3>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-dark-panel text-slate-400 border border-dark-border">
          {files.length} match{files.length !== 1 ? 'es' : ''}
        </span>
      </div>

      {files.length === 0 ? (
        <p className="text-xs text-slate-400 py-3 text-center">No candidate source files matching search criteria.</p>
      ) : (
        <div className="space-y-4">
          {files.map((file, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-dark-card border border-dark-border hover:border-slate-600 transition-colors space-y-3"
            >
              {/* Card Header */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2 font-mono text-xs font-semibold text-slate-200">
                  <Code2 className="w-4 h-4 text-brand-cyan" />
                  <span className="text-white hover:text-brand-cyan transition-colors">{file.path}</span>
                  {file.line_start && (
                    <span className="text-slate-400 text-[11px] bg-dark-bg px-1.5 py-0.5 rounded border border-dark-border">
                      L{file.line_start}{file.line_end ? `-L${file.line_end}` : ''}
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  {getBadge(file.evidence_type)}
                  {file.url && (
                    <a
                      href={file.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 rounded hover:bg-dark-panel text-slate-400 hover:text-white transition-colors"
                      title="View file on GitHub"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>

              {/* Symbols tag list */}
              {file.symbols.length > 0 && (
                <div className="flex flex-wrap gap-1.5 text-[11px] font-mono">
                  {file.symbols.map((sym, sIdx) => (
                    <span key={sIdx} className="px-2 py-0.5 rounded bg-dark-bg text-brand-violet border border-brand-violet/20">
                      {sym}
                    </span>
                  ))}
                </div>
              )}

              {/* Reason */}
              <p className="text-xs text-slate-300 font-sans">{file.reason}</p>

              {/* Excerpt Snippet */}
              {file.excerpt && (
                <div className="p-3 rounded-lg bg-[#080B10] border border-dark-border text-slate-300 font-mono text-xs overflow-x-auto">
                  <pre className="whitespace-pre">{file.excerpt}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
