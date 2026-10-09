import React, { useState } from 'react';
import { Search, Loader2, AlertCircle, ArrowRight } from 'lucide-react';

interface IssueInputFormProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
  error: string | null;
}

export const IssueInputForm: React.FC<IssueInputFormProps> = ({ onSubmit, isLoading, error }) => {
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    const trimmed = url.trim();
    if (!trimmed) {
      setValidationError('Please enter a GitHub issue URL.');
      return;
    }

    if (trimmed.includes('/pull/')) {
      setValidationError('The URL provided is a Pull Request. RepoXray requires a GitHub Issue URL (e.g. https://github.com/owner/repo/issues/123).');
      return;
    }

    const githubRegex = /^https?:\/\/(?:www\.)?github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/issues\/\d+\/?$/i;
    if (!githubRegex.test(trimmed)) {
      setValidationError('Invalid format. URL must be a public GitHub issue (e.g. https://github.com/owner/repo/issues/123).');
      return;
    }

    onSubmit(trimmed);
  };

  const displayError = validationError || error;

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-3">
      <div className="relative flex items-center">
        <div className="absolute left-4 text-slate-400 pointer-events-none">
          <Search className="w-5 h-5" />
        </div>

        <input
          type="url"
          value={url}
          onChange={(e) => {
            setUrl(e.target.value);
            if (validationError) setValidationError(null);
          }}
          placeholder="Paste a public GitHub issue URL (e.g. https://github.com/fastapi/fastapi/issues/1000)"
          disabled={isLoading}
          className="w-full pl-12 pr-40 py-4 rounded-xl bg-dark-surface border border-dark-border text-white placeholder-slate-500 focus:outline-none focus:border-brand-violet focus:ring-2 focus:ring-brand-violet/20 font-mono text-sm transition-all shadow-inner"
        />

        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="absolute right-2 top-2 bottom-2 px-5 rounded-lg bg-gradient-to-r from-brand-violet to-brand-indigo hover:from-brand-indigo hover:to-brand-violet text-white font-semibold text-sm flex items-center space-x-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-glow-violet"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Investigating...</span>
            </>
          ) : (
            <>
              <span>Investigate Issue</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {displayError && (
        <div className="flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-medium text-left animate-fadeIn">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{displayError}</span>
        </div>
      )}
    </form>
  );
};
