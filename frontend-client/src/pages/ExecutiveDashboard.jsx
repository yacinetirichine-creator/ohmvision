/**
 * OhmVision - Executive Dashboard
 * Tableau de bord exécutif avec KPIs et insights IA
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { apiUrl } from '../services/apiBase';
import {
  TrendingUp, TrendingDown, AlertTriangle, Users, Shield, 
  Camera, Clock, DollarSign, Activity, Download,
  BarChart2, PieChart, ChevronRight, Bell,
  Zap, Target, AlertCircle
} from 'lucide-react';

const ExecutiveDashboard = () => {
  const { t } = useTranslation();
  const [period, setPeriod] = useState('today');
  const [kpis, setKpis] = useState(null);
  const [_trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const [kpisRes, trendsRes] = await Promise.all([
        fetch(apiUrl(`/advanced/executive/kpis?period=${period}`)),
        fetch(apiUrl('/advanced/executive/trends?days=30'))
      ]);
      
      setKpis(await kpisRes.json());
      setTrends(await trendsRes.json());
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    }
    setLoading(false);
  }, [period]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('executiveDashboard.title')}</h1>
          <p className="text-gray-500">{t('executiveDashboard.subtitle')}</p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Période */}
          <select 
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 border rounded-lg bg-white"
          >
            <option value="today">{t('executiveDashboard.period.today')}</option>
            <option value="week">{t('executiveDashboard.period.week')}</option>
            <option value="month">{t('executiveDashboard.period.month')}</option>
          </select>
          
          {/* Export */}
          <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            <Download size={18} />
            {t('executiveDashboard.actions.exportPdf')}
          </button>
        </div>
      </div>

      {/* KPIs Principaux */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard 
          title={t('executiveDashboard.kpis.main.totalAlerts')}
          value={kpis?.kpis?.total_alerts?.value || 0}
          trend={kpis?.kpis?.total_alerts?.trend_pct}
          icon={AlertTriangle}
          color="orange"
        />
        <KPICard 
          title={t('executiveDashboard.kpis.main.criticalAlerts')}
          value={kpis?.kpis?.critical_alerts?.value || 0}
          trend={kpis?.kpis?.critical_alerts?.trend_pct}
          icon={AlertCircle}
          color="red"
        />
        <KPICard 
          title={t('executiveDashboard.kpis.main.uptime')}
          value={`${kpis?.kpis?.uptime?.value || 0}%`}
          trend={kpis?.kpis?.uptime?.trend}
          icon={Activity}
          color="green"
        />
        <KPICard 
          title={t('executiveDashboard.kpis.main.responseTime')}
          value={`${kpis?.kpis?.avg_response_time?.value || 0}s`}
          trend={kpis?.kpis?.avg_response_time?.trend}
          icon={Clock}
          color="blue"
          invertTrend
        />
      </div>

      {/* KPIs Secondaires */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard 
          title={t('executiveDashboard.kpis.secondary.ppeCompliance')}
          value={`${kpis?.kpis?.ppe_compliance?.value || 0}%`}
          trend={kpis?.kpis?.ppe_compliance?.trend}
          icon={Shield}
          color="purple"
        />
        <KPICard 
          title={t('executiveDashboard.kpis.secondary.visitors')}
          value={kpis?.kpis?.visitor_count?.value || 0}
          trend={kpis?.kpis?.visitor_count?.trend_pct}
          icon={Users}
          color="cyan"
        />
        <KPICard 
          title={t('executiveDashboard.kpis.secondary.incidentsPrevented')}
          value={kpis?.kpis?.incidents_prevented?.value || 0}
          trend={kpis?.kpis?.incidents_prevented?.trend}
          icon={Target}
          color="emerald"
        />
        <KPICard 
          title={t('executiveDashboard.kpis.secondary.savings')}
          value={`${(kpis?.kpis?.cost_savings?.value || 0).toLocaleString()}€`}
          trend={kpis?.kpis?.cost_savings?.trend}
          icon={DollarSign}
          color="yellow"
        />
      </div>

      {/* Graphiques et Détails */}
      <div className="grid grid-cols-3 gap-6">
        {/* Alertes par Sévérité */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <PieChart size={20} className="text-purple-600" />
            {t('executiveDashboard.charts.alertsBySeverity.title')}
          </h3>
          
          <div className="space-y-3">
            <AlertBar 
              label={t('executiveDashboard.charts.alertsBySeverity.critical')} 
              value={kpis?.alerts_by_severity?.critical || 0} 
              total={kpis?.kpis?.total_alerts?.value || 1}
              color="red"
            />
            <AlertBar 
              label={t('executiveDashboard.charts.alertsBySeverity.high')} 
              value={kpis?.alerts_by_severity?.high || 0} 
              total={kpis?.kpis?.total_alerts?.value || 1}
              color="orange"
            />
            <AlertBar 
              label={t('executiveDashboard.charts.alertsBySeverity.warnings')} 
              value={kpis?.alerts_by_severity?.warning || 0} 
              total={kpis?.kpis?.total_alerts?.value || 1}
              color="yellow"
            />
          </div>
        </div>

        {/* Top Caméras */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Camera size={20} className="text-purple-600" />
            {t('executiveDashboard.sections.topCameras')}
          </h3>
          
          <div className="space-y-3">
            {kpis?.top_cameras?.map((cam, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 flex items-center justify-center bg-purple-100 text-purple-600 rounded-full text-sm font-medium">
                    {i + 1}
                  </span>
                  <span className="text-gray-700">{cam.name}</span>
                </div>
                <span className="text-gray-500 font-medium">{t('executiveDashboard.common.alertsCount', { count: cam.alerts })}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Incidents Récents */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Bell size={20} className="text-purple-600" />
            {t('executiveDashboard.sections.recentIncidents')}
          </h3>
          
          <div className="space-y-3">
            {kpis?.recent_incidents?.map((incident, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${
                    incident.status === 'resolved' ? 'bg-green-500' :
                    incident.status === 'investigating' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></span>
                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {incident.type.toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-500">{incident.camera}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-400">{incident.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Insights IA */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-6 text-white">
        <h3 className="font-semibold text-xl mb-4 flex items-center gap-2">
          <Zap size={24} />
          {t('executiveDashboard.insights.title')}
        </h3>
        
        <div className="grid grid-cols-3 gap-4">
          <InsightCard 
            title={t('executiveDashboard.insights.cards.activitySpike.title')}
            description={t('executiveDashboard.insights.cards.activitySpike.description')}
            type="warning"
          />
          <InsightCard 
            title={t('executiveDashboard.insights.cards.ppeImprovement.title')}
            description={t('executiveDashboard.insights.cards.ppeImprovement.description')}
            type="success"
          />
          <InsightCard 
            title={t('executiveDashboard.insights.cards.riskZone.title')}
            description={t('executiveDashboard.insights.cards.riskZone.description')}
            type="alert"
          />
        </div>
      </div>

      {/* Actions Rapides */}
      <div className="grid grid-cols-4 gap-4">
        <ActionCard 
          title={t('executiveDashboard.quickActions.generateReport.title')}
          description={t('executiveDashboard.quickActions.generateReport.description')}
          icon={Download}
          onClick={() => window.open(apiUrl('/advanced/reports/daily/' + new Date().toISOString().split('T')[0]))}
        />
        <ActionCard 
          title={t('executiveDashboard.quickActions.viewAllAlerts.title')}
          description={t('executiveDashboard.quickActions.viewAllAlerts.description')}
          icon={AlertTriangle}
          onClick={() => window.location.href = '/alerts'}
        />
        <ActionCard 
          title={t('executiveDashboard.quickActions.configureNotifications.title')}
          description={t('executiveDashboard.quickActions.configureNotifications.description')}
          icon={Bell}
          onClick={() => window.location.href = '/settings#notifications'}
        />
        <ActionCard 
          title={t('executiveDashboard.quickActions.industryAnalytics.title')}
          description={t('executiveDashboard.quickActions.industryAnalytics.description')}
          icon={BarChart2}
          onClick={() => window.location.href = '/analytics'}
        />
      </div>
    </div>
  );
};

// Composants auxiliaires

const KPICard = ({ title, value, trend, icon: Icon, color, invertTrend = false }) => {
  const isPositive = invertTrend ? trend < 0 : trend > 0;
  const isNegative = invertTrend ? trend > 0 : trend < 0;
  
  const colorClasses = {
    orange: 'bg-orange-50 text-orange-600',
    red: 'bg-red-50 text-red-600',
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
    cyan: 'bg-cyan-50 text-cyan-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    yellow: 'bg-yellow-50 text-yellow-600'
  };
  
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <span className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon size={20} />
        </span>
        {trend !== undefined && trend !== null && (
          <span className={`flex items-center text-sm ${
            isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500'
          }`}>
            {isPositive ? <TrendingUp size={16} /> : isNegative ? <TrendingDown size={16} /> : null}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500">{title}</p>
    </div>
  );
};

const AlertBar = ({ label, value, total, color }) => {
  const percentage = (value / total) * 100;
  
  const colorClasses = {
    red: 'bg-red-500',
    orange: 'bg-orange-500',
    yellow: 'bg-yellow-500'
  };
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="text-gray-800 font-medium">{value}</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className={`h-full ${colorClasses[color]} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

const InsightCard = ({ title, description, type }) => {
  const typeClasses = {
    warning: 'bg-yellow-500/20 border-yellow-300',
    success: 'bg-green-500/20 border-green-300',
    alert: 'bg-red-500/20 border-red-300'
  };
  
  return (
    <div className={`p-4 rounded-lg border ${typeClasses[type]}`}>
      <h4 className="font-semibold mb-2">{title}</h4>
      <p className="text-sm text-white/80">{description}</p>
    </div>
  );
};

const ActionCard = ({ title, description, icon: Icon, onClick }) => (
  <button 
    onClick={onClick}
    className="bg-white rounded-xl p-5 shadow-sm text-left hover:shadow-md transition-shadow group"
  >
    <div className="flex justify-between items-center mb-2">
      <Icon size={24} className="text-purple-600" />
      <ChevronRight size={20} className="text-gray-400 group-hover:text-purple-600 transition-colors" />
    </div>
    <p className="font-semibold text-gray-900">{title}</p>
    <p className="text-sm text-gray-500">{description}</p>
  </button>
);

export default ExecutiveDashboard;
