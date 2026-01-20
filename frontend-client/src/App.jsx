import React, { useCallback, useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './services/store';
import { useTranslation } from 'react-i18next';

// Layouts
import AppLayout from './components/layout/AppLayout';
import AuthLayout from './components/layout/AuthLayout';

// Pages
import LandingPage from './pages/LandingPage';
import { GDPRPage, LegalMentionsPage, PrivacyPage, CGUPage, CGVPage, ContractPolicyPage } from './pages/LegalPages';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ModernDashboard from './pages/ModernDashboard';
import Cameras from './pages/Cameras';
import CameraView from './pages/CameraView';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import AIAssistant from './pages/AIAssistant';
import SetupWizard from './pages/SetupWizard';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import NotificationsConfig from './pages/NotificationsConfig';

// Protected Route
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  const [showSetup, setShowSetup] = useState(null); // null = loading, true = show, false = hide
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  const checkSetupStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/setup/status');
      const data = await response.json();
      
      // Afficher le wizard si c'est la première exécution
      setShowSetup(data.is_first_run && !data.setup_completed);
      setLoading(false);
    } catch (err) {
      console.error('Error checking setup status:', err);
      // En cas d'erreur, afficher l'app normale
      setShowSetup(false);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkSetupStatus();
  }, [checkSetupStatus]);

  const handleSetupComplete = () => {
    setShowSetup(false);
    // Recharger la page pour appliquer les changements
    window.location.href = '/';
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  // Show Setup Wizard if first run
  if (showSetup) {
    return <SetupWizard onComplete={handleSetupComplete} />;
  }

  return (
    <Routes>
      {/* Landing Page (Public) */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/legal/gdpr" element={<GDPRPage />} />
      <Route path="/legal/mentions" element={<LegalMentionsPage />} />
      <Route path="/legal/privacy" element={<PrivacyPage />} />
      <Route path="/legal/cgu" element={<CGUPage />} />
      <Route path="/legal/cgv" element={<CGVPage />} />
      <Route path="/legal/contract" element={<ContractPolicyPage />} />
      
      {/* Setup route (accessible manuellement) */}
      <Route path="/setup" element={<SetupWizard onComplete={handleSetupComplete} />} />
      
      {/* Auth routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
      </Route>
      
      {/* Protected routes */}
      <Route element={
        <ProtectedRoute>
          <AppLayout />
        </ProtectedRoute>
      }>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/modern" element={<ModernDashboard />} />
        <Route path="/executive" element={<ExecutiveDashboard />} />
        <Route path="/cameras" element={<Cameras />} />
        <Route path="/cameras/:id" element={<CameraView />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/ai" element={<AIAssistant />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/notifications" element={<NotificationsConfig />} />
      </Route>
      
      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
