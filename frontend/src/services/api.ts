import axios from 'axios';
import {
  ModelStatusResponse,
  InvestigationStatusResponse,
  InvestigationReport,
  AgentTraceStep
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  checkHealth: async () => {
    const res = await client.get('/api/health');
    return res.data;
  },

  getModelStatus: async (): Promise<ModelStatusResponse> => {
    const res = await client.get('/api/model/status');
    return res.data;
  },

  startInvestigation: async (issueUrl: string): Promise<{ investigation_id: string; status: string; message: string }> => {
    const res = await client.post('/api/investigations', { issue_url: issueUrl });
    return res.data;
  },

  getInvestigationStatus: async (id: string): Promise<InvestigationStatusResponse> => {
    const res = await client.get(`/api/investigations/${id}`);
    return res.data;
  },

  getInvestigationTrace: async (id: string): Promise<{ investigation_id: string; trace: AgentTraceStep[] }> => {
    const res = await client.get(`/api/investigations/${id}/trace`);
    return res.data;
  },

  getInvestigationReport: async (id: string): Promise<InvestigationReport> => {
    const res = await client.get(`/api/investigations/${id}/report`);
    return res.data;
  },

  cancelInvestigation: async (id: string) => {
    const res = await client.post(`/api/investigations/${id}/cancel`);
    return res.data;
  }
};
