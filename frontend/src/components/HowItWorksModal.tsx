import React from 'react';
import { X, HelpCircle, Search, Code2, TestTube2, ShieldCheck } from 'lucide-react';

interface HowItWorksModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HowItWorksModal: React.FC<HowItWorksModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-2xl p-6 rounded-2xl border border-dark-border shadow-2xl space-y-6 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-dark-panel transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-brand-cyan/20 text-brand-cyan flex items-center justify-center">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">How RepoXray Works</h3>
            <p className="text-xs text-slate-400">Autonomous 4-step GitHub evidence investigation</p>
          </div>
        </div>

        <div className="space-y-4 text-xs text-slate-300">
          <div className="p-4 rounded-xl bg-dark-card border border-dark-border space-y-2">
            <div className="flex items-center space-x-2 text-white font-bold text-sm">
              <Search className="w-4 h-4 text-brand-violet" />
              <span>1. GitHub Issue Retrieval</span>
            </div>
            <p className="leading-relaxed">
              When you paste an issue URL, RepoXray parses owner, repository name, and issue number. It queries the GitHub REST API to fetch live issue metadata (title, body, state, assignee, labels, timestamps).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-dark-card border border-dark-border space-y-2">
            <div className="flex items-center space-x-2 text-white font-bold text-sm">
              <Code2 className="w-4 h-4 text-brand-indigo" />
              <span>2. Safe Repository Indexing & BM25 Retrieval</span>
            </div>
            <p className="leading-relaxed">
              RepoXray acquires a snapshot of the public repository, safely extracts files without path traversal, parses Python AST symbols (<code className="text-brand-violet">def</code>, <code className="text-brand-violet">class</code>), normalizes identifier casing (<code className="text-brand-cyan">snake_case</code> & <code className="text-brand-cyan">camelCase</code>), and builds an in-memory BM25 Okapi search index.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-dark-card border border-dark-border space-y-2">
            <div className="flex items-center space-x-2 text-white font-bold text-sm">
              <TestTube2 className="w-4 h-4 text-brand-cyan" />
              <span>3. Registered Tool Agent Execution Loop</span>
            </div>
            <p className="leading-relaxed">
              Gemma 4 model selects investigative tools (such as <code className="text-brand-cyan">search_code</code>, <code className="text-brand-cyan">read_file</code>, <code className="text-brand-cyan">find_tests</code>, <code className="text-brand-cyan">find_linked_prs</code>, <code className="text-brand-cyan">read_contributing_guide</code>) up to a strict step execution bound. Every tool call executes real backend search operations and streams live trace events to the UI.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-dark-card border border-dark-border space-y-2">
            <div className="flex items-center space-x-2 text-white font-bold text-sm">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>4. Evidence Verification & Contribution Roadmap</span>
            </div>
            <p className="leading-relaxed">
              Before presenting the final report, RepoXray verifies every cited file path against the indexed repository snapshot. Unverified model recommendations are automatically flagged or removed. A conflict check detects assigned contributors or open PRs, and an actionable step-by-step roadmap is produced.
            </p>
          </div>
        </div>

        <div className="pt-2 text-right">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-brand-violet hover:bg-brand-indigo text-xs font-semibold text-white transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};
