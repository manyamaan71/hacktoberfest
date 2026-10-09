import React from 'react';
import { ExternalLink, CircleDot, Tag, User, GitCommit, ShieldAlert } from 'lucide-react';
import { IssueMetadata } from '../types';

interface IssueOverviewCardProps {
  issue: IssueMetadata;
}

export const IssueOverviewCard: React.FC<IssueOverviewCardProps> = ({ issue }) => {
  return (
    <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-4">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-dark-border/60 pb-3">
        <div className="flex items-center space-x-2">
          <CircleDot className={`w-5 h-5 ${issue.state === 'open' ? 'text-emerald-400' : 'text-purple-400'}`} />
          <span className="text-xs font-mono font-semibold text-slate-400">
            {issue.owner} / <strong className="text-white">{issue.repository}</strong> #{issue.number}
          </span>
          <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded-full border ${
            issue.state === 'open'
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
              : 'bg-purple-500/10 text-purple-400 border-purple-500/30'
          }`}>
            {issue.state}
          </span>
        </div>

        <a
          href={issue.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-dark-surface hover:bg-dark-panel border border-dark-border text-xs text-brand-cyan hover:underline transition-colors font-mono"
        >
          <span>View on GitHub</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Issue Title */}
      <div>
        <h2 className="text-xl font-bold text-white font-sans">{issue.title}</h2>
        {issue.commit_sha && (
          <div className="flex items-center space-x-1.5 text-xs text-slate-400 mt-1 font-mono">
            <GitCommit className="w-3.5 h-3.5 text-brand-violet" />
            <span>Analyzed Commit:</span>
            <span className="text-slate-300 bg-dark-panel px-1.5 py-0.5 rounded">{issue.commit_sha.substring(0, 7)}</span>
          </div>
        )}
      </div>

      {/* Labels & Assignee */}
      <div className="flex flex-wrap items-center gap-3 pt-1 text-xs">
        {issue.assignee && (
          <div className="flex items-center space-x-1.5 bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2.5 py-1 rounded-md">
            <User className="w-3.5 h-3.5" />
            <span>Assigned: @{issue.assignee}</span>
          </div>
        )}

        {issue.labels.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <Tag className="w-3.5 h-3.5 text-slate-400" />
            {issue.labels.map((label) => (
              <span
                key={label}
                className="px-2 py-0.5 rounded bg-dark-panel border border-dark-border text-slate-300 text-[11px] font-medium"
              >
                {label}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Excerpt Body */}
      {issue.body && (
        <div className="p-3 rounded-lg bg-dark-bg/80 border border-dark-border text-slate-300 text-xs font-mono max-h-32 overflow-y-auto whitespace-pre-wrap">
          {issue.body.slice(0, 500)}
          {issue.body.length > 500 && '...'}
        </div>
      )}
    </div>
  );
};
