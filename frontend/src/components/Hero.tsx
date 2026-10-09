import React from 'react';
import { Search, Sparkles, Code2, TestTube2, ShieldCheck } from 'lucide-react';
import { IssueInputForm } from './IssueInputForm';

interface HeroProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
  error: string | null;
}

export const Hero: React.FC<HeroProps> = ({ onSubmit, isLoading, error }) => {
  const exampleUrls = [
    { label: 'fastapi/fastapi #1000', url: 'https://github.com/fastapi/fastapi/issues/1000' },
    { label: 'psf/requests #5000', url: 'https://github.com/psf/requests/issues/5000' },
  ];

  return (
    <div className="relative overflow-hidden py-12 lg:py-16 px-4">
      {/* Background Subtle Gradient Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-brand-violet/20 via-brand-indigo/10 to-brand-cyan/20 blur-[120px] pointer-events-none rounded-full" />

      <div className="max-w-4xl mx-auto text-center space-y-8 relative z-10">
        {/* Badge */}
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-brand-violet/10 border border-brand-violet/30 text-brand-violet text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Autonomous GitHub Repo Evidence Investigator</span>
        </div>

        {/* Headline */}
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-mono leading-tight">
          Understand any GitHub issue <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-violet via-brand-indigo to-brand-cyan">
            before you contribute.
          </span>
        </h1>

        {/* Supporting text */}
        <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          An evidence-driven AI agent that explores unfamiliar repositories, finds relevant code and tests, and creates a practical contribution roadmap—with verified proof.
        </p>

        {/* Issue Input Form */}
        <div className="pt-2">
          <IssueInputForm onSubmit={onSubmit} isLoading={isLoading} error={error} />
          
          {/* Preset Example Buttons */}
          <div className="mt-4 flex items-center justify-center space-x-2 text-xs text-slate-400">
            <span>Try sample issue:</span>
            {exampleUrls.map((sample) => (
              <button
                key={sample.url}
                onClick={() => onSubmit(sample.url)}
                disabled={isLoading}
                className="px-2.5 py-1 rounded-md bg-dark-surface hover:bg-dark-panel border border-dark-border hover:border-slate-500 text-slate-300 hover:text-white transition-colors"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        {/* CSS/SVG Visual Investigation Illustration */}
        <div className="pt-8">
          <div className="glass-panel p-6 rounded-2xl border border-dark-border shadow-2xl relative">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-left">
              <div className="p-4 rounded-xl bg-dark-bg/60 border border-dark-border space-y-2">
                <div className="w-8 h-8 rounded-lg bg-brand-violet/20 text-brand-violet flex items-center justify-center">
                  <Search className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">1. Issue Scan</h4>
                <p className="text-xs text-slate-400">Retrieves title, description, labels, and state via GitHub REST API.</p>
              </div>

              <div className="p-4 rounded-xl bg-dark-bg/60 border border-dark-border space-y-2">
                <div className="w-8 h-8 rounded-lg bg-brand-indigo/20 text-brand-indigo flex items-center justify-center">
                  <Code2 className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">2. BM25 Code Index</h4>
                <p className="text-xs text-slate-400">Indexes Python source files and extracts AST function & class symbols.</p>
              </div>

              <div className="p-4 rounded-xl bg-dark-bg/60 border border-dark-border space-y-2">
                <div className="w-8 h-8 rounded-lg bg-brand-cyan/20 text-brand-cyan flex items-center justify-center">
                  <TestTube2 className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">3. Test Discovery</h4>
                <p className="text-xs text-slate-400">Locates related test files and extracts test commands from CONTRIBUTING docs.</p>
              </div>

              <div className="p-4 rounded-xl bg-dark-bg/60 border border-dark-border space-y-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">4. Verified Roadmap</h4>
                <p className="text-xs text-slate-400">Generates conflict-checked contribution roadmap with proof links.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
