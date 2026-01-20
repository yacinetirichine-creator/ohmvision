/**
 * OhmVision - Camera View Page
 * Vue détaillée d'une caméra avec streaming et contrôles
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft, Settings, Maximize, AlertTriangle, Users,
  Play, Pause, RefreshCw, Download, Zap, Eye
} from 'lucide-react';
import { useCamerasStore, useAlertsStore, useUIStore } from '../services/store';
import LiveStream from '../components/LiveStream';

const CameraView = () => {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const videoContainerRef = useRef(null);
  
  const { selectedCamera, getCamera, updateDetectionConfig } = useCamerasStore();
  const { alerts, fetchAlerts } = useAlertsStore();
  const { addNotification } = useUIStore();
  
  const [_isFullscreen, setIsFullscreen] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [detectionConfig, setDetectionConfig] = useState({});
  const [stats, setStats] = useState({
    persons: 0,
    entries: 0,
    exits: 0,
    alerts: 0
  });

  const detectionLabels = {
    person_detection: t('cameraView.detections.person.label'),
    counting: t('cameraView.detections.counting.label'),
    fall_detection: t('cameraView.detections.fall.label'),
    ppe_detection: t('cameraView.detections.ppe.label'),
    fire_detection: t('cameraView.detections.fire.label')
  };
  
  useEffect(() => {
    getCamera(id);
    fetchAlerts({ camera_id: id, limit: 20 });
  }, [id]);
  
  useEffect(() => {
    if (selectedCamera?.detection_config) {
      setDetectionConfig(selectedCamera.detection_config);
    }
  }, [selectedCamera]);
  
  // Simulated real-time stats
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        persons: Math.floor(Math.random() * 10),
        entries: prev.entries + (Math.random() > 0.7 ? 1 : 0),
        exits: prev.exits + (Math.random() > 0.8 ? 1 : 0),
        alerts: prev.alerts
      }));
    }, 2000);
    return () => clearInterval(interval);
  }, []);
  
  const handleConfigChange = async (key, value) => {
    const newConfig = { ...detectionConfig, [key]: value };
    setDetectionConfig(newConfig);
    
    const result = await updateDetectionConfig(id, { [key]: value });
    if (result.success) {
      const featureLabel = detectionLabels[key] || key;
      addNotification({
        type: 'success',
        title: t('cameraView.notifications.configUpdated.title'),
        message: t('cameraView.notifications.configUpdated.message', {
          feature: featureLabel,
          state: value ? t('cameraView.common.enabled') : t('cameraView.common.disabled')
        })
      });
    }
  };
  
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoContainerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };
  
  const cameraAlerts = alerts.filter(a => a.camera_id === parseInt(id));
  
  if (!selectedCamera) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/cameras')}
            className="p-2 hover:bg-dark-700 rounded-lg"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-bold">{selectedCamera.name}</h1>
            <p className="text-sm text-gray-500">{selectedCamera.location}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
            selectedCamera.is_online ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'
          }`}>
            <span className={`w-2 h-2 rounded-full ${selectedCamera.is_online ? 'bg-success animate-pulse' : 'bg-danger'}`} />
            {selectedCamera.is_online ? t('cameraView.status.online') : t('cameraView.status.offline')}
          </span>
          
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded-lg ${showSettings ? 'bg-primary text-white' : 'hover:bg-dark-700'}`}
          >
            <Settings size={20} />
          </button>
        </div>
      </div>
      
      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Video Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div ref={videoContainerRef} className="relative bg-dark-800 rounded-2xl overflow-hidden">
            {/* Composant LiveStream */}
            <LiveStream
              cameraId={parseInt(id)}
              rtspUrl={selectedCamera.rtsp_url}
              name={selectedCamera.name}
              autoStart={isPlaying}
              fps={15}
              quality={70}
              showOverlay={true}
            />
            
            {/* Real-time stats overlay */}
            <div className="absolute top-4 right-4 bg-black/50 rounded-lg p-3 space-y-2 z-10">
              <div className="flex items-center gap-2 text-sm">
                <Users size={14} className="text-primary" />
                <span className="text-white">{t('cameraView.overlay.peopleCount', { count: stats.persons })}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-success">
                <span>↓ {stats.entries}</span>
                <span className="text-gray-500">|</span>
                <span className="text-warning">↑ {stats.exits}</span>
              </div>
            </div>
            
            {/* Detection badges */}
            {detectionConfig.person_detection && (
              <div className="absolute bottom-16 left-4 flex flex-wrap gap-2 z-10">
                {detectionConfig.fall_detection && (
                  <span className="bg-purple-600/80 text-white text-xs px-2 py-1 rounded">
                    {t('cameraView.badges.fall')}
                  </span>
                )}
                {detectionConfig.ppe_detection && (
                  <span className="bg-warning/80 text-white text-xs px-2 py-1 rounded">
                    {t('cameraView.badges.ppe')}
                  </span>
                )}
                {detectionConfig.fire_detection && (
                  <span className="bg-danger/80 text-white text-xs px-2 py-1 rounded">
                    {t('cameraView.badges.fire')}
                  </span>
                )}
              </div>
            )}
            
            {/* Controls */}
            <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-4 z-10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="p-2 hover:bg-white/20 rounded-lg text-white"
                  >
                    {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                  </button>
                  <button 
                    onClick={() => window.location.reload()}
                    className="p-2 hover:bg-white/20 rounded-lg text-white"
                  >
                    <RefreshCw size={20} />
                  </button>
                </div>
                
                <div className="flex items-center gap-2">
                  <a 
                    href={`/api/streaming/snapshot/${id}?quality=95`}
                    download={`snapshot-${selectedCamera.name}.jpg`}
                    className="p-2 hover:bg-white/20 rounded-lg text-white"
                  >
                    <Download size={20} />
                  </a>
                  <button
                    onClick={toggleFullscreen}
                    className="p-2 hover:bg-white/20 rounded-lg text-white"
                  >
                    <Maximize size={20} />
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-4 gap-3">
            <StatCard
              icon={Users}
              label={t('cameraView.quickStats.people')}
              value={stats.persons}
              color="primary"
            />
            <StatCard
              icon={ArrowLeft}
              label={t('cameraView.quickStats.entries')}
              value={stats.entries}
              color="success"
              rotate={-90}
            />
            <StatCard
              icon={ArrowLeft}
              label={t('cameraView.quickStats.exits')}
              value={stats.exits}
              color="warning"
              rotate={90}
            />
            <StatCard
              icon={AlertTriangle}
              label={t('cameraView.quickStats.alerts')}
              value={cameraAlerts.length}
              color="danger"
            />
          </div>
        </div>
        
        {/* Sidebar */}
        <div className="space-y-4">
          {/* Settings Panel */}
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-dark-800 rounded-2xl p-4"
            >
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Zap size={18} className="text-primary" />
                {t('cameraView.detections.title')}
              </h3>
              
              <div className="space-y-3">
                <ToggleOption
                  label={t('cameraView.detections.person.label')}
                  description={t('cameraView.detections.person.description')}
                  enabled={detectionConfig.person_detection}
                  onChange={(v) => handleConfigChange('person_detection', v)}
                />
                <ToggleOption
                  label={t('cameraView.detections.counting.label')}
                  description={t('cameraView.detections.counting.description')}
                  enabled={detectionConfig.counting}
                  onChange={(v) => handleConfigChange('counting', v)}
                />
                <ToggleOption
                  label={t('cameraView.detections.fall.label')}
                  description={t('cameraView.detections.fall.description')}
                  enabled={detectionConfig.fall_detection}
                  onChange={(v) => handleConfigChange('fall_detection', v)}
                />
                <ToggleOption
                  label={t('cameraView.detections.ppe.label')}
                  description={t('cameraView.detections.ppe.description')}
                  enabled={detectionConfig.ppe_detection}
                  onChange={(v) => handleConfigChange('ppe_detection', v)}
                />
                <ToggleOption
                  label={t('cameraView.detections.fire.label')}
                  description={t('cameraView.detections.fire.description')}
                  enabled={detectionConfig.fire_detection}
                  onChange={(v) => handleConfigChange('fire_detection', v)}
                />
              </div>
            </motion.div>
          )}
          
          {/* Recent Alerts */}
          <div className="bg-dark-800 rounded-2xl p-4">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle size={18} className="text-warning" />
              {t('cameraView.recentAlerts.title')}
            </h3>
            
            {cameraAlerts.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-4">
                {t('cameraView.recentAlerts.empty')}
              </p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {cameraAlerts.slice(0, 5).map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg border-l-4 ${
                      alert.severity === 'critical' ? 'bg-danger/10 border-danger' :
                      alert.severity === 'high' ? 'bg-warning/10 border-warning' :
                      'bg-dark-700 border-gray-600'
                    }`}
                  >
                    <p className="font-medium text-sm">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Camera Info */}
          <div className="bg-dark-800 rounded-2xl p-4">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Eye size={18} className="text-primary" />
              {t('cameraView.info.title')}
            </h3>
            
            <div className="space-y-3 text-sm">
              <InfoRow label={t('cameraView.info.ip')} value={selectedCamera.ip_address || t('common.na')} />
              <InfoRow label={t('cameraView.info.resolution')} value={`${selectedCamera.resolution_width || 1920}x${selectedCamera.resolution_height || 1080}`} />
              <InfoRow label={t('cameraView.info.fps')} value={selectedCamera.fps || 15} />
              <InfoRow label={t('cameraView.info.lastActivity')} value={selectedCamera.last_seen ? new Date(selectedCamera.last_seen).toLocaleString() : t('common.na')} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Components
const StatCard = ({ icon: Icon, label, value, color, rotate = 0 }) => (
  <div className="bg-dark-800 rounded-xl p-4 text-center">
    <Icon size={20} className={`mx-auto mb-2 text-${color}`} style={{ transform: `rotate(${rotate}deg)` }} />
    <p className="text-2xl font-bold">{value}</p>
    <p className="text-xs text-gray-500">{label}</p>
  </div>
);

const ToggleOption = ({ label, description, enabled, onChange }) => (
  <div className="flex items-center justify-between">
    <div>
      <p className="font-medium text-sm">{label}</p>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
    <button
      onClick={() => onChange(!enabled)}
      className={`w-12 h-6 rounded-full transition-colors ${enabled ? 'bg-primary' : 'bg-dark-600'}`}
    >
      <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
    </button>
  </div>
);

const InfoRow = ({ label, value }) => (
  <div className="flex justify-between">
    <span className="text-gray-500">{label}</span>
    <span className="font-medium">{value}</span>
  </div>
);

export default CameraView;
