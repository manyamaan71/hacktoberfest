import React from 'react';
import { AlertTriangle, CheckCircle2, GitPullRequest, UserCheck, Lock, ExternalLink } from 'lucide-react';
import { ConflictInfo } from '../types';

interface ConflictAlertCardProps {
  conflicts: ConflictInfo[];
}

export const ConflictAlertCard: React.FC<ConflictAlertCardProps> = ({ conflicts }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'CLOSED_ISSUE':
        return <Lock className="w-5 h-5 text-rose-400" />;
      case 'ASSIGNED_CONTRIBUTOR':
        return <UserCheck className="w-5 h-5 text-amber-400" />;
      case 'LINKED_PR':
        return <GitPullRequest className="w-5 h-5 text-amber-400" />;
      default:
        return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
    }
  };

  return (
    <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-4">
      <div className="flex items-center space-x-2 border-b border-dark-border/60 pb-3">
        <AlertTriangle className="w-5 h-5 text-amber-400" />
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Contribution Status & Conflict Analysis</h3>
      </div>

      <div className="space-y-3">
        {conflicts.map((conflict, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-xl border flex items-start space-x-3 ${
              conflict.severity === 'high'
                ? 'bg-rose-500/10 border-rose-500/30 text-rose-200'
                : conflict.severity === 'medium'
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-200'
                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
            }`}
          >
            <div className="flex-shrink-0 mt-0.5">{getIcon(conflict.type)}</div>
            <div className="space-y-1 text-xs">
              <h4 className="font-bold text-white text-sm">{conflict.title}</h4>
              <p className="leading-relaxed opacity-90">{conflict.description}</p>

              {conflict.linked_pr_urls && conflict.linked_pr_urls.length > 0 && (
                <div className="pt-2 space-y-1">
                  <span className="font-semibold text-slate-300">Linked Pull Requests:</span>
                  <div className="space-y-1">
                    {conflict.linked_pr_urls.map((prUrl, pIdx) => (
                      <a
                        key={pIdx}
                        href={prUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1.5 text-brand-cyan hover:underline font-mono"
                      >
                        <span>{prUrl}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
