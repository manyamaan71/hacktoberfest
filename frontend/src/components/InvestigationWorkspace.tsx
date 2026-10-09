import React, { useEffect, useState } from 'react';
import { Loader2, AlertCircle, ArrowLeft, XCircle, ShieldAlert, FileText, Download, X } from 'lucide-react';
import { InvestigationStatusResponse, InvestigationReport, AgentTraceStep } from '../types';
import { api } from '../services/api';
import { IssueOverviewCard } from './IssueOverviewCard';
import { SummaryCard } from './SummaryCard';
import { SourceFileCard } from './SourceFileCard';
import { TestExplorerCard } from './TestExplorerCard';
import { ConflictAlertCard } from './ConflictAlertCard';
import { RoadmapCard } from './RoadmapCard';
import { AgentTraceCard } from './AgentTraceCard';

interface InvestigationWorkspaceProps {
  status: InvestigationStatusResponse | null;
  report: InvestigationReport | null;
  trace: AgentTraceStep[];
  onBackToSearch: () => void;
  onCancel: () => void;
}

export const InvestigationWorkspace: React.FC<InvestigationWorkspaceProps> = ({
  status,
  report,
  trace,
  onBackToSearch,
  onCancel
}) => {
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null);
  const isScanning = status?.status === 'queued' || status?.status === 'indexing' || status?.status === 'investigating';
  const isFailed = status?.status === 'failed';
  const isCancelled = status?.status === 'cancelled';

  useEffect(() => () => {
    if (pdfPreviewUrl) URL.revokeObjectURL(pdfPreviewUrl);
  }, [pdfPreviewUrl]);

  const generatePdf = async () => {
    if (!report) return;
    setIsGeneratingPdf(true);
    setPdfError(null);
    try {
      const pdf = await api.getInvestigationPdf(report.investigation_id);
      const previewUrl = URL.createObjectURL(pdf);
      setPdfPreviewUrl(previewUrl);
    } catch (err: unknown) {
      setPdfError(err instanceof Error ? err.message : 'Could not generate the PDF report.');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const closePdfPreview = () => setPdfPreviewUrl(null);
  const pdfFilename = report
    ? `repoxray-${report.issue.owner}-${report.issue.repository}-${report.issue.number}.pdf`
    : 'repoxray-report.pdf';

  return (
    <div className="max-w-7xl mx-auto py-6 px-4 lg:px-6 space-y-6 animate-fadeIn">
      {/* Top Bar Navigation */}
      <div className="flex items-center justify-between border-b border-dark-border pb-4">
        <button
          onClick={onBackToSearch}
          className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-dark-surface hover:bg-dark-panel border border-dark-border text-xs font-semibold text-slate-300 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>New Search</span>
        </button>

        <div className="flex items-center space-x-2">
          {report && (
            <button
              onClick={() => void generatePdf()}
              disabled={isGeneratingPdf}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-emerald hover:bg-brand-indigo border border-brand-emerald/40 text-white text-xs font-semibold transition-colors disabled:opacity-60 disabled:cursor-wait"
            >
              {isGeneratingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
              <span>{isGeneratingPdf ? 'Generating PDF...' : 'Generate PDF Report'}</span>
            </button>
          )}
          {isScanning && (
            <button
              onClick={onCancel}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-semibold transition-colors"
            >
              <XCircle className="w-4 h-4" />
              <span>Cancel Investigation</span>
            </button>
          )}
        </div>
      </div>

      {/* Scanning Active View */}
      {isScanning && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-dark-border space-y-4 text-center">
            <div className="w-12 h-12 rounded-2xl bg-brand-cyan/20 text-brand-cyan flex items-center justify-center mx-auto shadow-glow-cyan">
              <Loader2 className="w-6 h-6 animate-spin" />
            </div>

            <div>
              <h3 className="text-xl font-bold text-white">Investigating Repository Evidence</h3>
              <p className="text-xs text-slate-400 mt-1">{status?.current_step || 'Initializing agent tool execution...'}</p>
            </div>

            {/* Progress Bar */}
            <div className="max-w-md mx-auto space-y-1.5">
              <div className="w-full h-2.5 rounded-full bg-dark-bg border border-dark-border overflow-hidden p-0.5">
                <div
                  className="h-full bg-gradient-to-r from-brand-violet via-brand-indigo to-brand-cyan rounded-full transition-all duration-500"
                  style={{ width: `${status?.progress_percentage || 10}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] font-mono text-slate-400">
                <span>Issue Scanning</span>
                <span>BM25 Indexing</span>
                <span>Agent Tools</span>
              </div>
            </div>
          </div>

          {/* Live Streaming Agent Trace */}
          <AgentTraceCard trace={trace} isScanning={true} />
        </div>
      )}

      {/* Failed View */}
      {isFailed && (
        <div className="glass-panel p-8 rounded-2xl border border-rose-500/40 bg-rose-500/5 space-y-4 text-center max-w-xl mx-auto">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Investigation Error</h3>
          <p className="text-xs text-rose-300 font-mono bg-dark-bg p-3 rounded-lg border border-rose-500/30">
            {status?.error_message || 'An unexpected error occurred during investigation.'}
          </p>
          <button
            onClick={onBackToSearch}
            className="px-5 py-2.5 rounded-xl bg-brand-violet hover:bg-brand-indigo text-white font-semibold text-xs transition-all shadow-glow-violet"
          >
            Try Another Issue
          </button>
        </div>
      )}

      {/* Cancelled View */}
      {isCancelled && (
        <div className="glass-panel p-6 rounded-2xl border border-amber-500/40 text-center max-w-md mx-auto space-y-3">
          <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
          <h3 className="text-base font-bold text-white">Investigation Cancelled</h3>
          <p className="text-xs text-slate-400">The investigation task was manually cancelled.</p>
          <button
            onClick={onBackToSearch}
            className="px-4 py-2 rounded-lg bg-dark-panel text-xs text-slate-200 font-semibold hover:text-white"
          >
            Return to Dashboard
          </button>
        </div>
      )}

      {/* Completed Report View */}
      {report && (
        <div className="space-y-6">
          {pdfError && (
            <div role="alert" className="flex items-start justify-between gap-3 rounded-lg border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-400">
              <span>{pdfError}</span>
              <button onClick={() => setPdfError(null)} aria-label="Dismiss PDF error">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Section A: Issue Overview */}
          <IssueOverviewCard issue={report.issue} />

          {/* Section B & E: Grid layout for Executive Summary and Contribution Status */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SummaryCard summary={report.summary} uncertainties={report.uncertainties} />
            <ConflictAlertCard conflicts={report.possible_conflicts} />
          </div>

          {/* Section F: Contribution Roadmap */}
          <RoadmapCard steps={report.contribution_steps} contributingCommand={report.contributing_command} />

          {/* Section C & D: Source files & Tests */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SourceFileCard files={report.relevant_files} />
            <TestExplorerCard tests={report.relevant_tests} />
          </div>

          {/* Section G: Live Agent Trace */}
          <AgentTraceCard trace={report.agent_trace} isScanning={false} />

          {/* Section H: Warnings & Limitations */}
          {(report.warnings.length > 0 || report.limitations.length > 0) && (
            <div className="glass-panel p-5 rounded-xl border border-dark-border space-y-3">
              <div className="flex items-center space-x-2 text-slate-300 font-bold text-xs uppercase tracking-wider">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                <span>Warnings & Analysis Limitations</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-xs text-slate-400">
                {report.warnings.map((w, idx) => (
                  <li key={`w-${idx}`} className="text-amber-300/90">{w}</li>
                ))}
                {report.limitations.map((l, idx) => (
                  <li key={`l-${idx}`}>{l}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {pdfPreviewUrl && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-3 backdrop-blur-sm sm:p-6"
          role="dialog"
          aria-modal="true"
          aria-label="PDF report preview"
        >
          <div className="flex h-[92vh] w-full max-w-6xl flex-col overflow-hidden rounded-2xl border border-dark-border bg-dark-surface shadow-2xl">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-dark-border px-4 py-3 sm:px-6">
              <div className="flex items-center gap-2 text-dark-bg">
                <FileText className="h-5 w-5 text-brand-emerald" />
                <h2 className="text-sm font-bold text-white sm:text-base">Investigation PDF Preview</h2>
              </div>
              <div className="flex items-center gap-2">
                <a
                  href={pdfPreviewUrl}
                  download={pdfFilename}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-emerald px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-brand-indigo"
                >
                  <Download className="h-4 w-4" />
                  Download PDF
                </a>
                <button
                  onClick={closePdfPreview}
                  className="rounded-lg border border-dark-border p-2 text-slate-300 transition-colors hover:bg-dark-panel hover:text-white"
                  aria-label="Close PDF preview"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
            <iframe
              src={pdfPreviewUrl}
              title="RepoXray investigation PDF report"
              className="min-h-0 flex-1 bg-white"
            />
          </div>
        </div>
      )}
    </div>
  );
};
