import React, { useState } from 'react';
import { Terminal, CheckCircle2, Loader2, Circle, AlertCircle, ChevronDown, ChevronRight, Clock } from 'lucide-react';
import { AgentTraceStep } from '../types';

interface AgentTraceCardProps {
  trace: AgentTraceStep[];
  isScanning?: boolean;
}

export const AgentTraceCard: React.FC<AgentTraceCardProps> = ({ trace, isScanning }) => {
  const [expandedSteps, setExpandedSteps] = useState<Record<number, boolean>>({});

  const toggleExpand = (stepNum: number) => {
    setExpandedSteps((prev) => ({ ...prev, [stepNum]: !prev[stepNum] }));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-brand-cyan animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-rose-400" />;
      default:
        return <Circle className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-4">
      <div className="flex items-center justify-between border-b border-dark-border/60 pb-3">
        <div className="flex items-center space-x-2">
          <Terminal className="w-5 h-5 text-brand-cyan" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            LIVE AGENT INVESTIGATION TRACE
          </h3>
        </div>
        {isScanning && (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/30 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-brand-cyan animate-ping"></span>
            <span>Agent Active</span>
          </span>
        )}
      </div>

      {trace.length === 0 ? (
        <div className="py-6 text-center text-slate-400 text-xs space-y-2">
          <Loader2 className="w-5 h-5 animate-spin mx-auto text-brand-cyan" />
          <p>Agent initializing tool loop...</p>
        </div>
      ) : (
        <div className="space-y-2">
          {trace.map((step) => {
            const isExpanded = expandedSteps[step.step_number] || false;
            return (
              <div
                key={step.step_number}
                className="rounded-lg bg-dark-card border border-dark-border overflow-hidden text-xs transition-colors"
              >
                {/* Step Header */}
                <div
                  onClick={() => toggleExpand(step.step_number)}
                  className="p-3 flex items-center justify-between cursor-pointer hover:bg-dark-panel transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(step.status)}
                    <span className="font-mono font-bold text-brand-violet">
                      Step #{step.step_number}
                    </span>
                    <span className="font-mono font-semibold text-white px-2 py-0.5 rounded bg-dark-bg border border-dark-border">
                      {step.tool_name}
                    </span>
                    <span className="text-slate-300 font-sans truncate max-w-xs md:max-w-md">
                      {step.action_description}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-slate-400">
                    {step.duration_ms && (
                      <span className="flex items-center space-x-1 font-mono text-[11px]">
                        <Clock className="w-3 h-3" />
                        <span>{step.duration_ms}ms</span>
                      </span>
                    )}
                    {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="p-3 bg-dark-bg/90 border-t border-dark-border space-y-2 font-mono text-[11px]">
                    {step.input_summary && Object.keys(step.input_summary).length > 0 && (
                      <div>
                        <span className="text-slate-400 font-bold uppercase">Arguments:</span>
                        <pre className="p-2 mt-1 rounded bg-[#07090F] text-brand-cyan overflow-x-auto">
                          {JSON.stringify(step.input_summary, null, 2)}
                        </pre>
                      </div>
                    )}

                    {step.result_summary && (
                      <div>
                        <span className="text-slate-400 font-bold uppercase">Result:</span>
                        <p className="p-2 mt-1 rounded bg-[#07090F] text-slate-200">
                          {step.result_summary}
                        </p>
                      </div>
                    )}

                    {step.error_message && (
                      <div className="text-rose-400">
                        <span className="font-bold uppercase">Error:</span>
                        <p className="p-2 mt-1 rounded bg-rose-500/10 border border-rose-500/30">
                          {step.error_message}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
