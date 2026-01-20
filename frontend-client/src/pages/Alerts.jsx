/**
 * OhmVision - Alerts Page
 * Gestion et visualisation des alertes
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  Bell, AlertTriangle, CheckCircle, Filter, Search, Check, X, Camera,
  Flame, User, Shield, Car, Clock
} from 'lucide-react';
import { useAlertsStore, useCamerasStore } from '../services/store';

const Alerts = () => {
  const { alerts, fetchAlerts, markAsRead, markAllAsRead, resolveAlert, isLoading } = useAlertsStore();
  const { cameras, fetchCameras } = useCamerasStore();
  const { t } = useTranslation();
  
  const [filters, setFilters] = useState({
    type: '',
    severity: '',
    status: '',
    camera: ''
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  
  useEffect(() => {
    fetchAlerts({ limit: 100 });
    fetchCameras();
  }, []);
  
  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    if (filters.type && alert.type !== filters.type) return false;
    if (filters.severity && alert.severity !== filters.severity) return false;
    if (filters.status === 'unread' && alert.is_read) return false;
    if (filters.status === 'read' && !alert.is_read) return false;
    if (filters.status === 'resolved' && !alert.is_resolved) return false;
    if (filters.camera && alert.camera_id !== parseInt(filters.camera)) return false;
    if (searchQuery && !alert.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });
  
  // Group by date
  const groupedAlerts = filteredAlerts.reduce((groups, alert) => {
    const date = new Date(alert.created_at).toLocaleDateString();
    if (!groups[date]) groups[date] = [];
    groups[date].push(alert);
    return groups;
  }, {});
  
  const alertTypes = [
    { value: 'person_detected', label: t('alerts.types.person_detected'), icon: User },
    { value: 'fall_detected', label: t('alerts.types.fall_detected'), icon: AlertTriangle },
    { value: 'ppe_missing', label: t('alerts.types.ppe_missing'), icon: Shield },
    { value: 'fire_detected', label: t('alerts.types.fire_detected'), icon: Flame },
    { value: 'intrusion', label: t('alerts.types.intrusion'), icon: AlertTriangle },
    { value: 'vehicle_detected', label: t('alerts.types.vehicle_detected'), icon: Car },
  ];
  
  const severityColors = {
    critical: 'bg-danger text-danger',
    high: 'bg-warning text-warning',
    medium: 'bg-primary text-primary',
    low: 'bg-gray-500 text-gray-400'
  };
  
  const getAlertIcon = (type) => {
    const alertType = alertTypes.find(t => t.value === type);
    return alertType?.icon || Bell;
  };
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{t('alerts.title')}</h1>
          <p className="text-gray-500">
            {t('alerts.unreadSummary', {
              unread: filteredAlerts.filter(a => !a.is_read).length,
              total: filteredAlerts.length
            })}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={markAllAsRead}
            className="px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg text-sm flex items-center gap-2"
          >
            <CheckCircle size={16} />
            {t('alerts.actions.markAllRead')}
          </button>
        </div>
      </div>
      
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder={t('alerts.searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-800 border border-dark-500 rounded-xl focus:outline-none focus:border-primary"
          />
        </div>
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`px-4 py-2.5 rounded-xl flex items-center gap-2 ${
            showFilters ? 'bg-primary text-white' : 'bg-dark-800 hover:bg-dark-700'
          }`}
        >
          <Filter size={18} />
          {t('alerts.filters.button')}
          {Object.values(filters).some(v => v) && (
            <span className="w-2 h-2 bg-primary rounded-full" />
          )}
        </button>
      </div>
      
      {/* Filter Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4 bg-dark-800 rounded-xl">
              <select
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                className="px-3 py-2 bg-dark-700 rounded-lg text-sm focus:outline-none"
              >
                <option value="">{t('alerts.filters.allTypes')}</option>
                {alertTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
              
              <select
                value={filters.severity}
                onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                className="px-3 py-2 bg-dark-700 rounded-lg text-sm focus:outline-none"
              >
                <option value="">{t('alerts.filters.allSeverities')}</option>
                <option value="critical">{t('alerts.severity.critical')}</option>
                <option value="high">{t('alerts.severity.high')}</option>
                <option value="medium">{t('alerts.severity.medium')}</option>
                <option value="low">{t('alerts.severity.low')}</option>
              </select>
              
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="px-3 py-2 bg-dark-700 rounded-lg text-sm focus:outline-none"
              >
                <option value="">{t('alerts.filters.allStatuses')}</option>
                <option value="unread">{t('alerts.status.unread')}</option>
                <option value="read">{t('alerts.status.read')}</option>
                <option value="resolved">{t('alerts.status.resolved')}</option>
              </select>
              
              <select
                value={filters.camera}
                onChange={(e) => setFilters({ ...filters, camera: e.target.value })}
                className="px-3 py-2 bg-dark-700 rounded-lg text-sm focus:outline-none"
              >
                <option value="">{t('alerts.filters.allCameras')}</option>
                {cameras.map(cam => (
                  <option key={cam.id} value={cam.id}>{cam.name}</option>
                ))}
              </select>
              
              <button
                onClick={() => setFilters({ type: '', severity: '', status: '', camera: '' })}
                className="col-span-2 md:col-span-4 px-3 py-2 text-sm text-gray-400 hover:text-white"
              >
                {t('alerts.filters.reset')}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Alerts List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-20 bg-dark-800 rounded-xl skeleton" />
          ))}
        </div>
      ) : filteredAlerts.length === 0 ? (
        <div className="text-center py-12 bg-dark-800 rounded-xl">
          <Bell size={48} className="mx-auto mb-4 text-gray-600" />
          <p className="text-gray-500">{t('alerts.empty')}</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedAlerts).map(([date, dateAlerts]) => (
            <div key={date}>
              <h3 className="text-sm text-gray-500 mb-3 flex items-center gap-2">
                <Clock size={14} />
                {date === new Date().toLocaleDateString() ? t('alerts.date.today') : date}
              </h3>
              
              <div className="space-y-2">
                {dateAlerts.map((alert) => {
                  const Icon = getAlertIcon(alert.type);
                  const camera = cameras.find(c => c.id === alert.camera_id);
                  
                  return (
                    <motion.div
                      key={alert.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`
                        p-4 bg-dark-800 rounded-xl border-l-4 cursor-pointer
                        hover:bg-dark-700 transition-colors
                        ${severityColors[alert.severity]?.split(' ')[0] || 'border-gray-600'}
                        ${!alert.is_read ? 'ring-1 ring-primary/30' : ''}
                      `}
                      onClick={() => {
                        setSelectedAlert(alert);
                        if (!alert.is_read) markAsRead(alert.id);
                      }}
                    >
                      <div className="flex items-start gap-4">
                        <div className={`
                          w-10 h-10 rounded-xl flex items-center justify-center
                          ${severityColors[alert.severity]?.split(' ')[0]}/20
                        `}>
                          <Icon size={20} className={severityColors[alert.severity]?.split(' ')[1]} />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`
                              px-2 py-0.5 rounded text-xs font-medium
                              ${severityColors[alert.severity]?.split(' ')[0]}/20
                              ${severityColors[alert.severity]?.split(' ')[1]}
                            `}>
                              {alert.severity}
                            </span>
                            {!alert.is_read && (
                              <span className="w-2 h-2 bg-primary rounded-full" />
                            )}
                            {alert.is_resolved && (
                              <span className="text-xs text-success flex items-center gap-1">
                                <CheckCircle size={12} />
                                {t('alerts.status.resolvedLabel')}
                              </span>
                            )}
                          </div>
                          
                          <p className="font-medium">{alert.message}</p>
                          
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                              <Camera size={14} />
                              {camera?.name || t('alerts.cameraFallback', { id: alert.camera_id })}
                            </span>
                            <span>
                              {new Date(alert.created_at).toLocaleTimeString()}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          {!alert.is_resolved && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                resolveAlert(alert.id);
                              }}
                              className="p-2 hover:bg-success/20 rounded-lg text-gray-400 hover:text-success"
                              title={t('alerts.actions.resolveTitle')}
                            >
                              <Check size={18} />
                            </button>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Alert Detail Modal */}
      <AnimatePresence>
        {selectedAlert && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedAlert(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-dark-800 rounded-2xl p-6 max-w-lg w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">{t('alerts.detail.title')}</h2>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="p-2 hover:bg-dark-700 rounded-lg"
                >
                  <X size={20} />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className={`
                  p-4 rounded-xl
                  ${severityColors[selectedAlert.severity]?.split(' ')[0]}/10
                `}>
                  <p className="font-medium text-lg">{selectedAlert.message}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">{t('alerts.detail.fields.type')}</p>
                    <p className="font-medium">{selectedAlert.type.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{t('alerts.detail.fields.severity')}</p>
                    <p className="font-medium capitalize">{selectedAlert.severity}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{t('alerts.detail.fields.date')}</p>
                    <p className="font-medium">{new Date(selectedAlert.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{t('alerts.detail.fields.camera')}</p>
                    <p className="font-medium">
                      {cameras.find(c => c.id === selectedAlert.camera_id)?.name || `#${selectedAlert.camera_id}`}
                    </p>
                  </div>
                </div>
                
                {selectedAlert.snapshot_url && (
                  <div>
                    <p className="text-sm text-gray-500 mb-2">{t('alerts.detail.fields.snapshot')}</p>
                    <img
                      src={selectedAlert.snapshot_url}
                      alt={t('alerts.detail.snapshotAlt')}
                      className="w-full rounded-lg"
                    />
                  </div>
                )}
                
                {selectedAlert.data && Object.keys(selectedAlert.data).length > 0 && (
                  <div>
                    <p className="text-sm text-gray-500 mb-2">{t('alerts.detail.fields.data')}</p>
                    <pre className="bg-dark-900 p-3 rounded-lg text-xs overflow-x-auto">
                      {JSON.stringify(selectedAlert.data, null, 2)}
                    </pre>
                  </div>
                )}
                
                <div className="flex gap-3 pt-4">
                  {!selectedAlert.is_resolved && (
                    <button
                      onClick={() => {
                        resolveAlert(selectedAlert.id);
                        setSelectedAlert(null);
                      }}
                      className="flex-1 px-4 py-2 bg-success hover:bg-success/80 rounded-lg flex items-center justify-center gap-2"
                    >
                      <Check size={18} />
                      {t('alerts.actions.markResolved')}
                    </button>
                  )}
                  <button
                    onClick={() => setSelectedAlert(null)}
                    className="px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg"
                  >
                    {t('common.close')}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Alerts;
