/**
 * API Service Layer for Pulselytics Frontend
 * Centralized API calls to Flask backend
 */

import axios from 'axios';

// Default to relative "/api" so Vite dev proxy forwards to the Flask backend.
// You can override with VITE_API_URL (e.g., http://127.0.0.1:5000/api) if needed.
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper: try primary path, fallback to alternate on 404
const requestWithFallback = async (primary, fallback, config = {}) => {
  try {
    // Ensure primary is relative so baseURL (e.g., /api) is applied
    const normalized = primary.startsWith('/') ? primary.slice(1) : primary;
    const res = await api.request({ url: normalized, ...config });
    // api interceptor already returns response.data, so res is the data
    return res;
  } catch (err) {
    const status = err.response?.status;
    if (status === 404 && fallback) {
      // retry with absolute URL to backend root in case baseURL carries /api
      const direct = API_BASE_URL.replace(/\/(api)\/?$/, '');
      const url = fallback.startsWith('http') ? fallback : `${direct}${fallback}`;
      const res = await axios.request({ url, ...config, headers: { 'Content-Type': 'application/json' } });
      return res.data;
    }
    throw err;
  }
};

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.error || error.message || 'API request failed';
    console.error('[API] Response error:', message);
    return Promise.reject(new Error(message));
  }
);

// ============================================================================
// CLIENT MANAGEMENT
// ============================================================================

export const getClients = async () => {
  try {
    const response = await requestWithFallback('clients', '/clients');
    return response.data?.clients || response.clients || [];
  } catch (error) {
    console.error('Failed to fetch clients:', error);
    return [];
  }
};

export const getClient = async (clientId) => {
  const response = await api.get(`clients/${clientId}`);
  return response.client;
};

export const createClient = async (clientData) => {
  const response = await requestWithFallback('clients', '/clients', { method: 'POST', data: clientData });
  return response.data?.client || response.client;
};

export const updateClient = async (clientId, clientData) => {
  const response = await requestWithFallback(`clients/${clientId}`, `/clients/${clientId}`, { method: 'PUT', data: clientData });
  return response.data?.client || response.client;
};

export const deleteClient = async (clientId) => {
  await requestWithFallback(`clients/${clientId}`, `/clients/${clientId}`, { method: 'DELETE' });
};

// ============================================================================
// ANALYTICS & DATA
// ============================================================================

export const getAnalytics = async (params = {}) => {
  const { client, range = '30days', platform = 'all', search = '' } = params;

  const response = await requestWithFallback(
    'analytics',
    '/analytics',
    { params: { client, range, platform, search }, method: 'GET' }
  );

  // Normalize different return shapes:
  // - Primary path (axios instance interceptor): response => { success, data }
  // - Fallback path (raw axios): response => { data: { success, data } }
  if (response && typeof response === 'object') {
    if (response.success && response.data) return response.data; // primary path
    if (response.data && response.data.data) return response.data.data; // fallback path
    // If backend returned the analytics object directly
    if (response.total_posts !== undefined) return response;
  }
  return {};
};

export const getClientPosts = async (clientId, params = {}) => {
  const { limit = 50, sort = 'upload_date' } = params;
  
  const response = await requestWithFallback(`clients/${clientId}/posts`, `/clients/${clientId}/posts`, { method: 'GET', params: { limit, sort } });
  // Normalize
  if (response && typeof response === 'object') {
    if (response.success && response.posts) return response.posts;
    if (response.data && response.data.posts) return response.data.posts;
    if (Array.isArray(response)) return response;
  }
  return [];
};

export const getSummaryStats = async () => {
  const response = await requestWithFallback('stats/summary', '/stats/summary');
  if (response && typeof response === 'object') {
    if (response.success && response.stats) return response.stats;
    if (response.data && response.data.stats) return response.data.stats;
  }
  return {};
};

// ============================================================================
// PROFILE SUGGESTIONS
// ============================================================================

export const getProfileSuggestions = async (platform, query = '') => {
  try {
    const response = await requestWithFallback('profiles/suggest', '/profiles/suggest', { 
      method: 'GET', 
      params: { platform, query } 
    });
    return response.data?.suggestions || response.suggestions || [];
  } catch (error) {
    console.error('Failed to fetch profile suggestions:', error);
    return [];
  }
};

// ============================================================================
// SCRAPING
// ============================================================================

export const triggerScrape = async (clientId, platforms = ['all']) => {
  const response = await requestWithFallback('scrape', '/scrape', { method: 'POST', data: { client_id: clientId, platforms } });
  
  return response.data || response;
};

export const getScraperStatus = async () => {
  const response = await requestWithFallback('schedule/status', '/schedule/status');
  return response.data || response;
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthCheck = async () => {
  try {
    const response = await api.get('health');
    return response;
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'error', error: error.message };
  }
};

// ============================================================================
// API KEY MANAGEMENT
// ============================================================================

export const getApiKeys = async () => {
  try {
    const response = await requestWithFallback('api-keys', '/api-keys');
    return response.data?.keys || response.keys || {};
  } catch (error) {
    console.error('Failed to fetch API keys:', error);
    return {};
  }
};

export const saveApiKey = async (platform, apiKey, apiSecret = null, accessToken = null) => {
  try {
    const response = await requestWithFallback(
      `api-keys/${platform}`, 
      `/api-keys/${platform}`, 
      { 
        method: 'POST', 
        data: { 
          api_key: apiKey,
          api_secret: apiSecret,
          access_token: accessToken
        } 
      }
    );
    return response.data || response;
  } catch (error) {
    console.error(`Failed to save ${platform} API key:`, error);
    throw error;
  }
};

export const validateApiKey = async (platform, apiKey) => {
  try {
    const response = await requestWithFallback(
      `api-keys/${platform}/validate`, 
      `/api-keys/${platform}/validate`, 
      { 
        method: 'POST', 
        data: { api_key: apiKey } 
      }
    );
    return response.data || response;
  } catch (error) {
    console.error(`Failed to validate ${platform} API key:`, error);
    throw error;
  }
};

export const deleteApiKey = async (platform) => {
  try {
    const response = await requestWithFallback(
      `api-keys/${platform}`, 
      `/api-keys/${platform}`, 
      { method: 'DELETE' }
    );
    return response.data || response;
  } catch (error) {
    console.error(`Failed to delete ${platform} API key:`, error);
    throw error;
  }
};

// ============================================================================
// EXPORT
// ============================================================================

export const generatePDFReport = async (clientId, dateRange = '30days') => {
  try {
    const response = await requestWithFallback(
      'reports/generate',
      '/reports/generate',
      {
        method: 'POST',
        data: {
          client_id: clientId,
          range: dateRange
        }
      }
    );
    return response.data || response;
  } catch (error) {
    console.error('Failed to generate PDF report:', error);
    throw error;
  }
};

// ============================================================================
// AI INSIGHTS
// ============================================================================

export const generateAIInsights = async (clientId, dateRange = '30days') => {
  try {
    const response = await requestWithFallback(
      'insights/generate',
      '/insights/generate',
      {
        method: 'POST',
        data: {
          client_id: clientId,
          range: dateRange
        }
      }
    );
    return response.data || response;
  } catch (error) {
    console.error('Failed to generate AI insights:', error);
    throw error;
  }
};

export const getContentRecommendations = async (clientId) => {
  try {
    const response = await requestWithFallback(
      'insights/content-recommendations',
      '/insights/content-recommendations',
      {
        method: 'POST',
        data: {
          client_id: clientId
        }
      }
    );
    return response.data || response;
  } catch (error) {
    console.error('Failed to get content recommendations:', error);
    throw error;
  }
};

// ============================================================================
// ML MODEL STATUS & DIAGNOSTICS
// ============================================================================

export const getMLModelStatus = async () => {
  // Direct call via axios instance; no alias fallback exists for these endpoints
  const response = await api.get('ml/models/status');
  return response;
};

export const getMLDiagnostics = async () => {
  const response = await api.get('ml/diagnostics');
  return response;
};

// ============================================================================
// ML - Anomalies
// ============================================================================

export const detectAnomalies = async (clientId) => {
  const response = await requestWithFallback(
    'ml/detect/anomalies',
    '/ml/detect/anomalies',
    { method: 'GET', params: { client_id: clientId } }
  );

  // Normalize shapes
  if (response && typeof response === 'object') {
    if (response.success) return response;
    if (response.data && response.data.success) return response.data;
  }
  return { success: false, anomalies: [], total_anomalies_found: 0 };
};

export default {
  // Clients
  getClients,
  getClient,
  createClient,
  updateClient,
  deleteClient,
  
  // Analytics
  getAnalytics,
  getClientPosts,
  getSummaryStats,
  
  // Profile suggestions
  getProfileSuggestions,
  
  // Scraping
  triggerScrape,
  getScraperStatus,
  
  // Health
  healthCheck,
  
  // API Keys
  getApiKeys,
  saveApiKey,
  validateApiKey,
  deleteApiKey,
  
  // Reports
  generatePDFReport,
  
  // AI Insights
  generateAIInsights,
  getContentRecommendations,
  // ML
  getMLModelStatus,
  getMLDiagnostics,
  detectAnomalies,
};
