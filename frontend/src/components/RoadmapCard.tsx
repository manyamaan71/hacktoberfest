import React, { useState } from 'react';
import { MapPin, CheckSquare, Square, Terminal, Code2, ArrowRight } from 'lucide-react';
import { ContributionStep } from '../types';

interface RoadmapCardProps {
  steps: ContributionStep[];
  contributingCommand?: string | null;
}

export const RoadmapCard: React.FC<RoadmapCardProps> = ({ steps, contributingCommand }) => {
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});

  const toggleStep = (stepNum: number) => {
    setCompletedSteps((prev) => ({ ...prev, [stepNum]: !prev[stepNum] }));
  };

  return (
    <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-4">
      <div className="flex items-center justify-between border-b border-dark-border/60 pb-3">
        <div className="flex items-center space-x-2">
          <MapPin className="w-5 h-5 text-brand-violet" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Contribution Investigation Roadmap</h3>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-brand-violet/10 text-brand-violet border border-brand-violet/30 font-medium">
          Step-by-step Plan
        </span>
      </div>

      {contributingCommand && (
        <div className="p-3 rounded-lg bg-dark-card border border-dark-border flex items-center justify-between font-mono text-xs">
          <div className="flex items-center space-x-2 text-slate-300">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span>Documented Test Command:</span>
            <code className="text-emerald-400 bg-dark-bg px-2 py-1 rounded border border-emerald-500/30">
              {contributingCommand}
            </code>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {steps.map((step) => {
          const isDone = completedSteps[step.step_number] || false;
          return (
            <div
              key={step.step_number}
              onClick={() => toggleStep(step.step_number)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isDone
                  ? 'bg-emerald-500/5 border-emerald-500/30 opacity-75'
                  : 'bg-dark-card border-dark-border hover:border-slate-600'
              }`}
            >
              <div className="flex items-start space-x-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleStep(step.step_number);
                  }}
                  className="mt-0.5 text-slate-400 hover:text-white transition-colors"
                >
                  {isDone ? (
                    <CheckSquare className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <Square className="w-5 h-5 text-slate-500" />
                  )}
                </button>

                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className={`text-sm font-bold ${isDone ? 'line-through text-slate-400' : 'text-white'}`}>
                      Step {step.step_number}: {step.title}
                    </h4>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-dark-bg text-slate-400 font-mono border border-dark-border">
                      {step.action_type}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed font-sans">{step.description}</p>

                  {step.target_files && step.target_files.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] text-slate-400 font-medium">Target Files:</span>
                      {step.target_files.map((tf, fIdx) => (
                        <span
                          key={fIdx}
                          className="px-2 py-0.5 rounded bg-dark-bg text-brand-cyan font-mono text-[11px] border border-brand-cyan/20"
                        >
                          {tf}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
