/**
 * OhmVision - Dashboard Page
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Camera,
  Bell,
  Users,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Activity,
  Eye,
  ChevronRight,
  Wifi,
  WifiOff,
  HardHat,
  Flame,
  Car
} from 'lucide-react';
import { useAnalyticsStore, useCamerasStore, useAlertsStore } from '../services/store';
import TutorialOverlay from '../components/TutorialOverlay';

// Stat Card Component (Futuristic Update)
const StatCard = ({ icon: Icon, label, value, trend, trendValue, color = 'primary' }) => {
  const colorClasses = {
    primary: 'text-ohm-cyan drop-shadow-[0_0_5px_rgba(0,240,255,0.5)]',
    success: 'text-success drop-shadow-[0_0_5px_rgba(34,197,94,0.5)]',
    warning: 'text-warning drop-shadow-[0_0_5px_rgba(245,158,11,0.5)]',
    danger: 'text-danger drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]',
    purple: 'text-ohm-purple drop-shadow-[0_0_5px_rgba(188,19,254,0.5)]'
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5 relative overflow-hidden group"
    >
      <div className="absolute top-0 right-0 p-8 bg-white/5 rounded-full blur-xl group-hover:bg-ohm-cyan/10 transition-colors duration-500"></div>
      
      <div className="flex items-start justify-between mb-4 relative z-10">
        <div className={`w-12 h-12 rounded-xl bg-dark-900/50 border border-white/10 flex items-center justify-center ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm font-mono ${trend === 'up' ? 'text-success' : 'text-danger'}`}>
            {trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span>{trendValue}</span>
          </div>
        )}
      </div>
      <p className="text-3xl font-bold mb-1 text-white tracking-tight">{value}</p>
      <p className="text-sm text-gray-400">{label}</p>
    </motion.div>
  );
};

// Camera Preview Card
const CameraCard = ({ camera }) => {
  return (
    <Link to={`/cameras/${camera.id}`}>
      <motion.div
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="glass-card overflow-hidden group"
      >
        {/* Video Preview */}
        <div className="relative aspect-video bg-dark-900">
          {/* Grid Overlay */}
          <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>

          {/* Placeholder - in production, show actual video thumbnail */}
          <div className="absolute inset-0 flex items-center justify-center">
            <Camera size={40} className="text-ohm-cyan/50" />
          </div>
          
          {/* Status indicator */}
          <div className={`absolute top-3 left-3 flex items-center gap-2 px-2 py-1 rounded-sm text-xs font-bold border ${
            camera.is_online
              ? 'bg-success/10 text-success border-success/30'
              : 'bg-danger/10 text-danger border-danger/30'
          }`}>
            {camera.is_online ? <Wifi size={12} /> : <WifiOff size={12} />}
            {camera.is_online ? 'ONLINE' : 'OFFLINE'}
          </div>
          
          {/* Live indicator */}
          {camera.is_online && (
            <div className="absolute top-3 right-3 flex items-center gap-1 px-2 py-1 bg-danger/80 backdrop-blur rounded-sm text-xs font-bold shadow-[0_0_10px_rgba(239,68,68,0.5)]">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
              LIVE
            </div>
          )}
          
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-ohm-cyan/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center border-2 border-ohm-cyan/50">
            <Eye size={32} className="text-white drop-shadow-[0_0_5px_rgba(0,240,255,1)]" />
          </div>
        </div>
        
        {/* Info */}
        <div className="p-4 bg-dark-850/50 backdrop-blur-sm">
          <h3 className="font-semibold truncate">{camera.name}</h3>
          <p className="text-sm text-gray-400 truncate">{camera.location || 'Aucun emplacement'}</p>
          
          {/* Detection badges */}
          <div className="flex gap-2 mt-3">
            {camera.detection_config?.person_detection && (
              <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                👤 Personnes
              </span>
            )}
            {camera.detection_config?.fall_detection && (
              <span className="px-2 py-1 bg-warning/10 text-warning text-xs rounded-full">
                ⬇️ Chute
              </span>
            )}
            {camera.detection_config?.ppe_detection && (
              <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">
                🦺 EPI
              </span>
            )}
          </div>
        </div>
      </motion.div>
    </Link>
  );
};

// Alert Item
const AlertItem = ({ alert }) => {
  const severityColors = {
    critical: 'border-danger bg-danger/5',
    high: 'border-warning bg-warning/5',
    medium: 'border-primary bg-primary/5',
    low: 'border-gray-500 bg-gray-500/5'
  };
  
  const typeIcons = {
    fall_detected: '⬇️',
    ppe_missing: '🦺',
    fire_detected: '🔥',
    intrusion: '🚨',
    person_detected: '👤',
    vehicle_detected: '🚗'
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`p-4 rounded-xl border-l-4 ${severityColors[alert.severity]}`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{typeIcons[alert.type] || '⚠️'}</span>
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{alert.message}</p>
          <p className="text-sm text-gray-400">
            {new Date(alert.created_at).toLocaleTimeString('fr-FR')}
          </p>
        </div>
        {!alert.is_read && (
          <span className="w-2 h-2 bg-primary rounded-full" />
        )}
      </div>
    </motion.div>
  );
};

// Quick Actions
const QuickActions = () => {
  const actions = [
    { icon: Camera, label: 'Ajouter caméra', color: 'primary', path: '/cameras?add=true' },
    { icon: HardHat, label: 'Vérifier EPI', color: 'success', path: '/analytics?type=ppe' },
    { icon: Users, label: 'Comptage', color: 'purple', path: '/analytics?type=counting' },
    { icon: Flame, label: 'Alertes feu', color: 'danger', path: '/alerts?type=fire' }
  ];
  
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {actions.map((action) => (
        <Link key={action.label} to={action.path}>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`p-4 rounded-xl bg-${action.color}/10 border border-${action.color}/20 flex flex-col items-center justify-center gap-2 hover:bg-${action.color}/20 transition-colors`}
          >
            <action.icon size={24} className={`text-${action.color}`} />
            <span className="text-sm font-medium text-center">{action.label}</span>
          </motion.div>
        </Link>
      ))}
    </div>
  );
};

// Main Dashboard
export default function Dashboard() {
  const { dashboard, fetchDashboard, isLoading } = useAnalyticsStore();
  const { cameras, fetchCameras } = useCamerasStore();
  const { alerts, fetchAlerts } = useAlertsStore();
  
  // Tutorial State
  const [showTutorial, setShowTutorial] = useState(false);

  useEffect(() => {
    fetchDashboard();
    fetchCameras();
    fetchAlerts({ limit: 5 });
    
    const hasSeenTutorial = localStorage.getItem('ohm_tutorial_seen');
    if (!hasSeenTutorial) {
        setTimeout(() => setShowTutorial(true), 1500);
    }
  }, []);

  const closeTutorial = () => {
      setShowTutorial(false);
      localStorage.setItem('ohm_tutorial_seen', 'true');
  };

  const tutorialSteps = [
      {
          title: "Bienvenue sur OhmVision",
          content: "Votre interface de sécurité v3.0 est prête. Ce tableau de bord centralise l'intelligence de votre site."
      },
      {
          title: "Indicateurs Clés",
          content: "Surveillez ici l'état de santé de vos caméras et le nombre d'alertes en temps réel."
      },
      {
          title: "Actions Rapides",
          content: "Lancez des analyses ou générez des rapports en un clic depuis cette barre d'actions."
      }
  ];
  
  const stats = dashboard || {
    cameras: { total: 0, online: 0, offline: 0 },
    alerts: { today: 0, critical: 0 },
    counting: { entries_today: 0, exits_today: 0 },
    ppe: { compliance_rate: 100 }
  };
  
  return (
    <div className="space-y-6">
      <TutorialOverlay isOpen={showTutorial} onClose={closeTutorial} steps={tutorialSteps} />

      {/* Welcome */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Bonjour ! 👋</h1>
          <p className="text-gray-400">Système de sécurité actif - <span className="text-ohm-cyan font-mono">v3.0.1</span></p>
        </div>
        <div className="hidden md:flex items-center gap-3">
          <button 
             onClick={() => setShowTutorial(true)}
             className="text-xs font-mono text-ohm-cyan/70 hover:text-ohm-cyan underline underline-offset-4"
          >
             TUTORIAL_MODE
          </button>
          <div className="px-3 py-1 rounded bg-success/10 border border-success/30 text-success text-sm flex items-center gap-2">
            <Activity size={16} />
            <span>SYSTÈME ONLINE</span>
          </div>
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Camera}
          label="Caméras en ligne"
          value={`${stats.cameras.online}/${stats.cameras.total}`}
          trend={stats.cameras.online === stats.cameras.total ? 'up' : 'down'}
          trendValue={`${Math.round((stats.cameras.online / stats.cameras.total) * 100) || 0}%`}
          color="success"
        />
        <StatCard
          icon={Bell}
          label="Alertes aujourd'hui"
          value={stats.alerts.today}
          color={stats.alerts.critical > 0 ? 'danger' : 'primary'}
        />
        <StatCard
          icon={Users}
          label="Entrées"
          value={stats.counting.entries_today}
          trend="up"
          trendValue="+12%"
          color="purple"
        />
        <StatCard
          icon={HardHat}
          label="Conformité EPI"
          value={`${stats.ppe.compliance_rate}%`}
          trend={stats.ppe.compliance_rate >= 90 ? 'up' : 'down'}
          trendValue={stats.ppe.compliance_rate >= 90 ? 'OK' : 'Attention'}
          color={stats.ppe.compliance_rate >= 90 ? 'success' : 'warning'}
        />
      </div>
      
      {/* Quick Actions */}
      <div>
        <h2 className="font-semibold mb-3">Actions rapides</h2>
        <QuickActions />
      </div>
      
      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Cameras */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Mes caméras</h2>
            <Link to="/cameras" className="text-primary text-sm flex items-center gap-1 hover:underline">
              Voir tout <ChevronRight size={16} />
            </Link>
          </div>
          
          {cameras.length === 0 ? (
            <div className="bg-dark-800 rounded-2xl p-8 text-center border border-dark-600">
              <Camera size={48} className="mx-auto text-gray-600 mb-4" />
              <h3 className="font-semibold mb-2">Aucune caméra</h3>
              <p className="text-gray-400 mb-4">Ajoutez votre première caméra pour commencer</p>
              <Link
                to="/cameras?add=true"
                className="inline-block bg-primary hover:bg-primary-dark text-white px-6 py-2 rounded-xl transition-colors"
              >
                Ajouter une caméra
              </Link>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-4">
              {cameras.slice(0, 4).map((camera) => (
                <CameraCard key={camera.id} camera={camera} />
              ))}
            </div>
          )}
        </div>
        
        {/* Alerts */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Alertes récentes</h2>
            <Link to="/alerts" className="text-primary text-sm flex items-center gap-1 hover:underline">
              Voir tout <ChevronRight size={16} />
            </Link>
          </div>
          
          <div className="space-y-3">
            {alerts.length === 0 ? (
              <div className="bg-dark-800 rounded-2xl p-6 text-center border border-dark-600">
                <Bell size={32} className="mx-auto text-gray-600 mb-3" />
                <p className="text-gray-400">Aucune alerte récente</p>
              </div>
            ) : (
              alerts.slice(0, 5).map((alert) => (
                <AlertItem key={alert.id} alert={alert} />
              ))
            )}
          </div>
          
          {/* Critical alert banner */}
          {stats.alerts.critical > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-4 p-4 bg-danger/10 border border-danger/30 rounded-xl"
            >
              <div className="flex items-center gap-3">
                <AlertTriangle className="text-danger" />
                <div>
                  <p className="font-semibold text-danger">
                    {stats.alerts.critical} alerte{stats.alerts.critical > 1 ? 's' : ''} critique{stats.alerts.critical > 1 ? 's' : ''}
                  </p>
                  <p className="text-sm text-gray-400">Action immédiate requise</p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
