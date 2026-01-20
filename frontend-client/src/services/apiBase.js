// Centralised API base handling for both axios and fetch usage.
// VITE_API_BASE should include the /api prefix, e.g. https://api.ohmvision.app/api

export const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '');

export const apiUrl = (path) => {
  if (!path) return API_BASE;
  if (typeof path !== 'string') return API_BASE;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  if (path.startsWith('/')) return `${API_BASE}${path}`;
  return `${API_BASE}/${path}`;
};
