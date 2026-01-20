/**
 * OhmVision Client - State Management & API Services
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';
import i18n from '../i18n';

const getPreferredLanguage = () => {
  const lang = localStorage.getItem('ohmvision_language');
  if (lang === 'fr' || lang === 'en' || lang === 'es') return lang;
  return 'fr';
};

// API Configuration
const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  config.headers['Accept-Language'] = getPreferredLanguage();
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Auth Store
// ============================================================================

export const useAuthStore = create(
  persist(
    (set, _get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const formData = new URLSearchParams();
          formData.append('username', email);
          formData.append('password', password);
          
          const { data } = await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
          });
          
          localStorage.setItem('token', data.access_token);
          set({
            user: data.user,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false
          });
          
          return { success: true };
        } catch (error) {
          set({
            error: error.response?.data?.detail || i18n.t('auth.errors.loginFailed'),
            isLoading: false
          });
          return { success: false, error: error.response?.data?.detail };
        }
      },
      
      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      },
      
      checkAuth: async () => {
        const token = localStorage.getItem('token');
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }
        
        try {
          const { data } = await api.get('/auth/me');
          set({ user: data, isAuthenticated: true, token });
        } catch {
          localStorage.removeItem('token');
          set({ user: null, token: null, isAuthenticated: false });
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user })
    }
  )
);

// ============================================================================
// Cameras Store
// ============================================================================

export const useCamerasStore = create((set, _get) => ({
  cameras: [],
  selectedCamera: null,
  isLoading: false,
  error: null,
  
  fetchCameras: async () => {
    set({ isLoading: true });
    try {
      const { data } = await api.get('/cameras');
      set({ cameras: data, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },
  
  getCamera: async (id) => {
    set({ isLoading: true });
    try {
      const { data } = await api.get(`/cameras/${id}`);
      set({ selectedCamera: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      return null;
    }
  },
  
  updateCamera: async (id, updates) => {
    try {
      const { data } = await api.put(`/cameras/${id}`, updates);
      set((state) => ({
        cameras: state.cameras.map((c) => (c.id === id ? data : c)),
        selectedCamera: state.selectedCamera?.id === id ? data : state.selectedCamera
      }));
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },
  
  updateDetectionConfig: async (id, config) => {
    try {
      await api.put(`/cameras/${id}/detection-config`, config);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}));

// ============================================================================
// Alerts Store
// ============================================================================

export const useAlertsStore = create((set, _get) => ({
  alerts: [],
  unreadCount: 0,
  isLoading: false,
  filters: {
    type: null,
    severity: null,
    isRead: null
  },
  
  fetchAlerts: async (options = {}) => {
    set({ isLoading: true });
    try {
      const params = new URLSearchParams();
      if (options.type) params.append('type', options.type);
      if (options.severity) params.append('severity', options.severity);
      if (options.camera_id) params.append('camera_id', options.camera_id);
      if (options.limit) params.append('limit', options.limit);
      
      const { data } = await api.get(`/alerts?${params}`);
      set({
        alerts: data.items || data,
        unreadCount: (data.items || data).filter((a) => !a.is_read).length,
        isLoading: false
      });
    } catch (error) {
      set({ isLoading: false });
    }
  },
  
  markAsRead: async (id) => {
    try {
      await api.put(`/alerts/${id}/read`);
      set((state) => ({
        alerts: state.alerts.map((a) => (a.id === id ? { ...a, is_read: true } : a)),
        unreadCount: state.unreadCount - 1
      }));
    } catch {}
  },
  
  markAllAsRead: async () => {
    try {
      await api.post('/alerts/mark-all-read');
      set((state) => ({
        alerts: state.alerts.map((a) => ({ ...a, is_read: true })),
        unreadCount: 0
      }));
    } catch {}
  },
  
  resolveAlert: async (id) => {
    try {
      await api.put(`/alerts/${id}/resolve`);
      set((state) => ({
        alerts: state.alerts.map((a) => (a.id === id ? { ...a, is_resolved: true } : a))
      }));
    } catch {}
  }
}));

// ============================================================================
// Analytics Store
// ============================================================================

export const useAnalyticsStore = create((set) => ({
  dashboard: null,
  counting: null,
  trends: null,
  isLoading: false,
  
  fetchDashboard: async () => {
    set({ isLoading: true });
    try {
      const { data } = await api.get('/analytics/dashboard');
      set({ dashboard: data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },
  
  fetchCounting: async (cameraId, options = {}) => {
    try {
      const params = new URLSearchParams();
      if (cameraId) params.append('camera_id', cameraId);
      if (options.start_date) params.append('start_date', options.start_date);
      if (options.end_date) params.append('end_date', options.end_date);
      
      const { data } = await api.get(`/analytics/counting?${params}`);
      set({ counting: data });
      return data;
    } catch {
      return null;
    }
  },
  
  fetchTrends: async (period = 'week') => {
    try {
      const { data } = await api.get(`/analytics/trends?period=${period}`);
      set({ trends: data });
      return data;
    } catch {
      return null;
    }
  }
}));

// ============================================================================
// AI Agent Store
// ============================================================================

export const useAIStore = create((set, _get) => ({
  messages: [],
  suggestions: [],
  isTyping: false,
  
  sendMessage: async (message, context = {}) => {
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    set((state) => ({
      messages: [...state.messages, userMessage],
      isTyping: true
    }));
    
    try {
      const { data } = await api.post('/ai/chat', { message, context });
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        actions: data.actions_taken,
        suggestions: data.suggestions,
        timestamp: new Date().toISOString()
      };
      
      set((state) => ({
        messages: [...state.messages, aiMessage],
        isTyping: false
      }));
      
      return data;
    } catch (error) {
      set({ isTyping: false });
      return { error: error.message };
    }
  },
  
  runDiagnostic: async (cameraId = null) => {
    try {
      const { data } = await api.post('/ai/diagnostic', { camera_id: cameraId });
      return data;
    } catch (error) {
      return { error: error.message };
    }
  },
  
  getSuggestions: async () => {
    try {
      const { data } = await api.get('/ai/suggestions');
      set({ suggestions: data.suggestions });
      return data.suggestions;
    } catch {
      return [];
    }
  },
  
  clearMessages: () => set({ messages: [] })
}));

// ============================================================================
// UI Store
// ============================================================================

export const useUIStore = create((set) => ({
  sidebarOpen: false,
  theme: 'dark',
  notifications: [],
  
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  closeSidebar: () => set({ sidebarOpen: false }),
  
  addNotification: (notification) => {
    const id = Date.now();
    set((state) => ({
      notifications: [...state.notifications, { ...notification, id }]
    }));
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id)
      }));
    }, 5000);
  },
  
  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id)
    }));
  }
}));

// Export API instance for direct use
export { api };
