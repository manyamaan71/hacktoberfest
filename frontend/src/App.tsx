import React, { useCallback, useState, useEffect } from 'react';
import axios from 'axios';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Hero } from './components/Hero';
import { InvestigationWorkspace } from './components/InvestigationWorkspace';
import { ModelStatusModal } from './components/ModelStatusModal';
import { HistoryDrawer } from './components/HistoryDrawer';
import { HowItWorksModal } from './components/HowItWorksModal';
import { api } from './services/api';
import {
  ModelStatusResponse,
  InvestigationStatusResponse,
  InvestigationReport,
  AgentTraceStep,
  HistoryItem
} from './types';

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    try {
      return localStorage.getItem('repoxray_theme') === 'dark' ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  });
  const [currentView, setCurrentView] = useState<'home' | 'workspace'>('home');
  const [modelStatus, setModelStatus] = useState<ModelStatusResponse | null>(null);
  
  const [investigationId, setInvestigationId] = useState<string | null>(null);
  const [status, setStatus] = useState<InvestigationStatusResponse | null>(null);
  const [report, setReport] = useState<InvestigationReport | null>(null);
  const [trace, setTrace] = useState<AgentTraceStep[]>([]);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Modals
  const [isModelModalOpen, setIsModelModalOpen] = useState(false);
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem('repoxray_theme', theme);
    } catch (err) {
      console.error('Failed to save theme preference:', err);
    }
  }, [theme]);

  // Local storage history
  const [history, setHistory] = useState<HistoryItem[]>(() => {
    try {
      const saved = localStorage.getItem('repoxray_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const loadModelStatus = useCallback(() => (
    api.getModelStatus()
      .then((res) => {
        setModelStatus(res);
      })
      .catch((err: unknown) => {
        console.error('Failed to load model status:', err);
      })
  ), []);

  // Load Model Status on mount
  useEffect(() => {
    void loadModelStatus();
  }, [loadModelStatus]);

  // Save history to localStorage
  const saveHistory = (items: HistoryItem[]) => {
    setHistory(items);
    try {
      localStorage.setItem('repoxray_history', JSON.stringify(items));
    } catch (err) {
      console.error('Failed to save history:', err);
    }
  };

  // Start Investigation
  const handleStartInvestigation = async (issueUrl: string) => {
    setSubmitError(null);
    setIsLoading(true);
    try {
      const res = await api.startInvestigation(issueUrl);
      setInvestigationId(res.investigation_id);
      setStatus({
        investigation_id: res.investigation_id,
        status: 'queued',
        progress_percentage: 5,
        current_step: 'Queued for investigation',
        issue_url: issueUrl
      });
      setReport(null);
      setTrace([]);
      setCurrentView('workspace');
    } catch (err: unknown) {
      const msg = axios.isAxiosError<{ detail?: string }>(err)
        ? err.response?.data?.detail || err.message
        : err instanceof Error
          ? err.message
          : 'Failed to start investigation.';
      setSubmitError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  // Polling loop for investigation progress
  useEffect(() => {
    if (!investigationId || !status) return;
    if (['completed', 'failed', 'cancelled'].includes(status.status)) return;

    const interval = setInterval(async () => {
      try {
        const statusRes = await api.getInvestigationStatus(investigationId);
        setStatus(statusRes);

        const traceRes = await api.getInvestigationTrace(investigationId);
        if (traceRes && traceRes.trace) {
          setTrace(traceRes.trace);
        }

        if (statusRes.status === 'completed') {
          clearInterval(interval);
          const reportRes = await api.getInvestigationReport(investigationId);
          setReport(reportRes);
          setTrace(reportRes.agent_trace);

          // Add to local history
          const newItem: HistoryItem = {
            id: investigationId,
            issue_url: reportRes.issue.url,
            title: reportRes.issue.title,
            repo: `${reportRes.issue.owner}/${reportRes.issue.repository}`,
            timestamp: new Date().toISOString(),
            status: 'completed'
          };
          
          const filtered = history.filter(h => h.id !== investigationId);
          saveHistory([newItem, ...filtered]);
        } else if (statusRes.status === 'failed' || statusRes.status === 'cancelled') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Error polling investigation status:', err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [investigationId, status, history]);

  // Select item from history
  const handleSelectHistoryItem = async (id: string) => {
    setInvestigationId(id);
    setIsLoading(true);
    try {
      const reportRes = await api.getInvestigationReport(id);
      setReport(reportRes);
      setStatus({
        investigation_id: id,
        status: 'completed',
        progress_percentage: 100,
        current_step: 'Completed',
        issue_url: reportRes.issue.url
      });
      setTrace(reportRes.agent_trace);
      setCurrentView('workspace');
    } catch (err) {
      console.error('Failed to load past report:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = async () => {
    if (investigationId) {
      try {
        await api.cancelInvestigation(investigationId);
        setStatus(prev => prev ? { ...prev, status: 'cancelled', current_step: 'Cancelled by user.' } : null);
      } catch (err) {
        console.error('Failed to cancel:', err);
      }
    }
  };

  const handleNewSearch = () => {
    setInvestigationId(null);
    setStatus(null);
    setReport(null);
    setTrace([]);
    setSubmitError(null);
    setCurrentView('home');
  };

  return (
    <div data-theme={theme} className="app-shell min-h-screen flex flex-col font-sans">
      <Navbar
        modelStatus={modelStatus}
        theme={theme}
        onToggleTheme={() => setTheme((current) => current === 'light' ? 'dark' : 'light')}
        onOpenModelModal={() => setIsModelModalOpen(true)}
        onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onNewInvestigation={handleNewSearch}
      />

      <div className="flex-1 flex">
        <Sidebar
          currentView={currentView}
          onNewInvestigation={handleNewSearch}
          onOpenHistory={() => setIsHistoryOpen(true)}
          onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
          onOpenModelModal={() => setIsModelModalOpen(true)}
          history={history}
          onSelectHistoryItem={handleSelectHistoryItem}
        />

        <main className="flex-1 overflow-x-hidden">
          {currentView === 'home' ? (
            <Hero
              onSubmit={handleStartInvestigation}
              isLoading={isLoading}
              error={submitError}
            />
          ) : (
            <InvestigationWorkspace
              status={status}
              report={report}
              trace={trace}
              onBackToSearch={handleNewSearch}
              onCancel={handleCancel}
            />
          )}
        </main>
      </div>

      {/* Modals & Drawers */}
      <ModelStatusModal
        isOpen={isModelModalOpen}
        onClose={() => setIsModelModalOpen(false)}
        status={modelStatus}
        onRefresh={loadModelStatus}
      />

      <HowItWorksModal
        isOpen={isHowItWorksOpen}
        onClose={() => setIsHowItWorksOpen(false)}
      />

      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelect={handleSelectHistoryItem}
        onClear={() => saveHistory([])}
      />
    </div>
  );
};

export default App;
