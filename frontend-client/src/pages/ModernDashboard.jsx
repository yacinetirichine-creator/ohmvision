/**
 * OhmVision - Modern Dashboard
 * Dashboard nouvelle génération avec visualisation live et analytics temps réel
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Camera, Bell, Activity, Users, Shield, Clock, AlertTriangle, Map, Settings, Filter,
  Sun
} from 'lucide-react';
import MultiCameraView from '../components/MultiCameraView';
import RealTimeStats from '../components/RealTimeStats';
import { useAuthStore } from '../services/store';

const getLocaleFromLanguage = (language) => {
  if (language?.startsWith('en')) return 'en-US';
  if (language?.startsWith('es')) return 'es-ES';
  return 'fr-FR';
};

// Header with time and weather
const DashboardHeader = ({ name }) => {
  const { t, i18n } = useTranslation();
  const [time, setTime] = useState(new Date());

  const locale = getLocaleFromLanguage(i18n.language);
  
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          {t('modernDashboard.header.greeting', { name: name || '—' })}
        </h1>
        <p className="text-gray-400 flex items-center gap-2">
          <Clock size={14} />
          {time.toLocaleDateString(locale, { 
            weekday: 'long', 
            day: 'numeric', 
            month: 'long' 
          })}
          <span className="text-primary font-mono">
            {time.toLocaleTimeString(locale)}
          </span>
        </p>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Weather widget */}
        <div className="hidden lg:flex items-center gap-3 px-4 py-2 rounded-xl bg-dark-800/50 backdrop-blur-sm border border-dark-700">
          <Sun size={20} className="text-yellow-400" />
          <div>
            <p className="text-sm font-medium text-white">23°C</p>
            <p className="text-xs text-gray-500">{t('modernDashboard.weather.city')}</p>
          </div>
        </div>
        
        {/* Quick actions */}
        <button className="p-3 rounded-xl bg-dark-800/50 backdrop-blur-sm border border-dark-700 hover:border-primary transition-colors">
          <Bell size={20} className="text-gray-400" />
        </button>
        
        <button className="p-3 rounded-xl bg-dark-800/50 backdrop-blur-sm border border-dark-700 hover:border-primary transition-colors">
          <Settings size={20} className="text-gray-400" />
        </button>
      </div>
    </div>
  );
};

// Quick stat pill
const QuickStat = ({ icon: Icon, value, label, color, pulse = false }) => (
  <div className={`
    flex items-center gap-3 px-4 py-3 rounded-xl
    bg-gradient-to-r ${color}
    border border-white/10
  `}>
    <div className={`p-2 rounded-lg bg-white/10 ${pulse ? 'animate-pulse' : ''}`}>
      <Icon size={18} className="text-white" />
    </div>
    <div>
      <p className="text-xl font-bold text-white">{value}</p>
      <p className="text-xs text-white/70">{label}</p>
    </div>
  </div>
);

// Site map placeholder
const SiteMapWidget = () => {
  const { t } = useTranslation();

  return (
    <div className="h-full rounded-2xl bg-dark-800/50 backdrop-blur-xl border border-dark-700 overflow-hidden">
      <div className="p-4 border-b border-dark-700">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Map size={16} className="text-primary" />
          {t('modernDashboard.siteMap.title')}
        </h3>
      </div>
      <div className="relative h-48 bg-dark-900">
        {/* Placeholder for site map */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <Map size={48} className="mx-auto mb-2 opacity-30" />
            <p className="text-sm">{t('modernDashboard.siteMap.placeholder.title')}</p>
            <p className="text-xs">{t('modernDashboard.siteMap.placeholder.subtitle')}</p>
          </div>
        </div>
        
        {/* Camera markers (simulated) */}
        <div className="absolute top-1/4 left-1/4 w-4 h-4 rounded-full bg-green-500 animate-ping opacity-50" />
        <div className="absolute top-1/4 left-1/4 w-3 h-3 rounded-full bg-green-500" />
        
        <div className="absolute top-1/2 right-1/3 w-4 h-4 rounded-full bg-green-500 animate-ping opacity-50" />
        <div className="absolute top-1/2 right-1/3 w-3 h-3 rounded-full bg-green-500" />
        
        <div className="absolute bottom-1/4 left-1/2 w-4 h-4 rounded-full bg-red-500 animate-ping opacity-50" />
        <div className="absolute bottom-1/4 left-1/2 w-3 h-3 rounded-full bg-red-500" />
      </div>
    </div>
  );
};

// Recent alerts widget
const RecentAlertsWidget = ({ alerts }) => {
  const { t } = useTranslation();

  return (
    <div className="h-full rounded-2xl bg-dark-800/50 backdrop-blur-xl border border-dark-700 overflow-hidden flex flex-col">
      <div className="p-4 border-b border-dark-700 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <AlertTriangle size={16} className="text-orange-400" />
          {t('modernDashboard.recentAlerts.title')}
        </h3>
        <button className="text-xs text-primary hover:underline">{t('modernDashboard.actions.viewAll')}</button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {alerts.map((alert, index) => (
          <div 
            key={index}
            className={`
              p-3 rounded-xl border-l-4
              ${alert.severity === 'critical' ? 'border-l-red-500 bg-red-500/10' :
                alert.severity === 'warning' ? 'border-l-orange-500 bg-orange-500/10' :
                'border-l-blue-500 bg-blue-500/10'}
            `}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{alert.title}</p>
                <p className="text-xs text-gray-400 mt-0.5">{alert.camera}</p>
              </div>
              <span className="text-xs text-gray-500 whitespace-nowrap">{alert.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// System health widget
const SystemHealthWidget = () => {
  const { t } = useTranslation();

  const systems = [
    { name: t('modernDashboard.systemHealth.systems.aiServer'), status: 'online', load: 45 },
    { name: t('modernDashboard.systemHealth.systems.database'), status: 'online', load: 32 },
    { name: t('modernDashboard.systemHealth.systems.storage'), status: 'warning', load: 78 },
    { name: t('modernDashboard.systemHealth.systems.network'), status: 'online', load: 15 },
  ];

  return (
    <div className="rounded-2xl bg-dark-800/50 backdrop-blur-xl border border-dark-700 p-4">
      <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
        <Activity size={16} className="text-primary" />
        {t('modernDashboard.systemHealth.title')}
      </h3>
      
      <div className="space-y-3">
        {systems.map((system, index) => (
          <div key={index} className="flex items-center gap-3">
            <div className={`
              w-2 h-2 rounded-full
              ${system.status === 'online' ? 'bg-green-500' :
                system.status === 'warning' ? 'bg-orange-500' :
                'bg-red-500'}
            `} />
            <span className="flex-1 text-sm text-gray-300">{system.name}</span>
            <div className="w-20 h-1.5 rounded-full bg-dark-600 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all ${
                  system.load > 70 ? 'bg-orange-500' :
                  system.load > 50 ? 'bg-yellow-500' :
                  'bg-green-500'
                }`}
                style={{ width: `${system.load}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 w-8 text-right">{system.load}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main Dashboard Component
const ModernDashboard = () => {
  const { t } = useTranslation();
  const { user } = useAuthStore();

  const displayName = user?.first_name || user?.email?.split('@')?.[0] || '—';

  // Mock cameras data
  const cameras = [
    { id: 1, name: 'Entrée Principale', location: 'Bâtiment A', recording: true },
    { id: 2, name: 'Parking Nord', location: 'Extérieur', recording: true },
    { id: 3, name: 'Hall Accueil', location: 'Bâtiment A', recording: false },
    { id: 4, name: 'Entrepôt', location: 'Bâtiment B', recording: true },
    { id: 5, name: 'Zone Production', location: 'Bâtiment C', recording: true },
    { id: 6, name: 'Sortie Secours', location: 'Bâtiment A', recording: false },
    { id: 7, name: 'Parking Sud', location: 'Extérieur', recording: true },
    { id: 8, name: 'Bureau Direction', location: 'Bâtiment A', recording: false },
  ];

  // Mock alerts data
  const alerts = [
    { title: t('modernDashboard.mockAlerts.intrusionDetected'), camera: 'Zone Production', severity: 'critical', time: t('modernDashboard.time.minutesAgo', { count: 2 }) },
    { title: t('modernDashboard.mockAlerts.ppeNonCompliant'), camera: 'Entrepôt', severity: 'warning', time: t('modernDashboard.time.minutesAgo', { count: 5 }) },
    { title: t('modernDashboard.mockAlerts.nightMovement'), camera: 'Parking Nord', severity: 'warning', time: t('modernDashboard.time.minutesAgo', { count: 12 }) },
    { title: t('modernDashboard.mockAlerts.longQueue'), camera: 'Hall Accueil', severity: 'info', time: t('modernDashboard.time.minutesAgo', { count: 18 }) },
    { title: t('modernDashboard.mockAlerts.unknownVehicle'), camera: 'Parking Sud', severity: 'info', time: t('modernDashboard.time.minutesAgo', { count: 25 }) },
  ];

  const [viewMode, setViewMode] = useState('split'); // 'split', 'cameras', 'stats'

  return (
    <div className="h-full flex flex-col">
      <DashboardHeader name={displayName} />
      
      {/* Quick stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <QuickStat 
          icon={Camera} 
          value="16/16" 
          label={t('modernDashboard.quickStats.camerasOnline')} 
          color="from-green-600/30 to-emerald-600/30"
        />
        <QuickStat 
          icon={Users} 
          value="47" 
          label={t('modernDashboard.quickStats.peopleDetected')} 
          color="from-blue-600/30 to-cyan-600/30"
        />
        <QuickStat 
          icon={AlertTriangle} 
          value="3" 
          label={t('modernDashboard.quickStats.activeAlerts')} 
          color="from-orange-600/30 to-amber-600/30"
          pulse
        />
        <QuickStat 
          icon={Shield} 
          value="94%" 
          label={t('modernDashboard.quickStats.ppeCompliance')} 
          color="from-purple-600/30 to-fuchsia-600/30"
        />
      </div>
      
      {/* View mode toggle */}
      <div className="flex items-center gap-2 mb-4">
        <div className="flex items-center p-1 rounded-xl bg-dark-800/50 backdrop-blur-sm border border-dark-700">
          <button
            onClick={() => setViewMode('split')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              viewMode === 'split' ? 'bg-primary text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            {t('modernDashboard.viewModes.split')}
          </button>
          <button
            onClick={() => setViewMode('cameras')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              viewMode === 'cameras' ? 'bg-primary text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            {t('modernDashboard.viewModes.cameras')}
          </button>
          <button
            onClick={() => setViewMode('stats')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              viewMode === 'stats' ? 'bg-primary text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            {t('modernDashboard.viewModes.analytics')}
          </button>
        </div>
        
        <div className="flex-1" />
        
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-dark-800/50 backdrop-blur-sm border border-dark-700 text-gray-400 hover:text-white transition-colors">
          <Filter size={16} />
          <span className="text-sm">{t('modernDashboard.filters.button')}</span>
        </button>
      </div>
      
      {/* Main content area */}
      <div className="flex-1 min-h-0">
        {viewMode === 'split' && (
          <div className="h-full grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Camera view - 2/3 */}
            <div className="lg:col-span-2 h-full min-h-[400px]">
              <MultiCameraView cameras={cameras} />
            </div>
            
            {/* Stats sidebar - 1/3 */}
            <div className="flex flex-col gap-4 overflow-y-auto">
              <RealTimeStats />
              <SystemHealthWidget />
            </div>
          </div>
        )}
        
        {viewMode === 'cameras' && (
          <div className="h-full">
            <MultiCameraView cameras={cameras} />
          </div>
        )}
        
        {viewMode === 'stats' && (
          <div className="h-full grid grid-cols-1 lg:grid-cols-2 gap-4 overflow-y-auto">
            <div className="space-y-4">
              <RealTimeStats />
            </div>
            <div className="space-y-4">
              <RecentAlertsWidget alerts={alerts} />
              <SiteMapWidget />
              <SystemHealthWidget />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModernDashboard;
