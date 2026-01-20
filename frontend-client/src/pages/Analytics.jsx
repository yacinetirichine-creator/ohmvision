/**
 * OhmVision - Analytics Page
 * Statistiques et graphiques
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  BarChart3, TrendingUp, TrendingDown, Users, AlertTriangle, Download, ArrowUp, ArrowDown
} from 'lucide-react';
import { AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { useAnalyticsStore, useCamerasStore } from '../services/store';

const Analytics = () => {
  const { t } = useTranslation();
  const { dashboard, counting, trends: _trends, fetchDashboard, fetchCounting, fetchTrends, isLoading: _isLoading } = useAnalyticsStore();
  const { cameras, fetchCameras } = useCamerasStore();
  
  const [period, setPeriod] = useState('week');
  const [selectedCamera, setSelectedCamera] = useState('');
  
  useEffect(() => {
    fetchDashboard();
    fetchCameras();
    fetchTrends(period);
    fetchCounting();
  }, [fetchCameras, fetchCounting, fetchDashboard, fetchTrends, period]);
  
  // Sample data for charts
  const hourlyData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}h`,
    entries: Math.floor(Math.random() * 50),
    exits: Math.floor(Math.random() * 45),
    persons: Math.floor(Math.random() * 30)
  }));

  const weeklyData = [
    t('analytics.weekDays.mon'),
    t('analytics.weekDays.tue'),
    t('analytics.weekDays.wed'),
    t('analytics.weekDays.thu'),
    t('analytics.weekDays.fri'),
    t('analytics.weekDays.sat'),
    t('analytics.weekDays.sun'),
  ].map((day) => ({
    day,
    entries: Math.floor(Math.random() * 200 + 50),
    exits: Math.floor(Math.random() * 190 + 45),
    alerts: Math.floor(Math.random() * 20)
  }));

  const alertsByType = [
    { key: 'persons', name: t('analytics.alertsByType.persons'), value: 45, color: '#3b82f6' },
    { key: 'falls', name: t('analytics.alertsByType.falls'), value: 5, color: '#ef4444' },
    { key: 'ppe', name: t('analytics.alertsByType.ppe'), value: 25, color: '#f59e0b' },
    { key: 'intrusion', name: t('analytics.alertsByType.intrusion'), value: 15, color: '#8b5cf6' },
    { key: 'fire', name: t('analytics.alertsByType.fire'), value: 2, color: '#ef4444' },
  ];
  
  const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6', '#22c55e'];
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{t('analytics.title')}</h1>
          <p className="text-gray-500">{t('analytics.subtitle')}</p>
        </div>
        
        <div className="flex items-center gap-3">
          <select
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
            className="px-4 py-2 bg-dark-800 border border-dark-500 rounded-lg text-sm focus:outline-none"
          >
            <option value="">{t('analytics.filters.allCameras')}</option>
            {cameras.map(cam => (
              <option key={cam.id} value={cam.id}>{cam.name}</option>
            ))}
          </select>
          
          <div className="flex bg-dark-800 rounded-lg p-1">
            {['day', 'week', 'month'].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-4 py-1.5 rounded-md text-sm ${
                  period === p ? 'bg-primary text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                {p === 'day'
                  ? t('analytics.periods.day')
                  : p === 'week'
                    ? t('analytics.periods.week')
                    : t('analytics.periods.month')}
              </button>
            ))}
          </div>
          
          <button className="p-2 bg-dark-800 hover:bg-dark-700 rounded-lg">
            <Download size={20} />
          </button>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title={t('analytics.stats.totalEntries')}
          value={counting?.total_entries || 1247}
          change={+12.5}
          icon={ArrowDown}
          color="success"
        />
        <StatCard
          title={t('analytics.stats.totalExits')}
          value={counting?.total_exits || 1198}
          change={+8.3}
          icon={ArrowUp}
          color="warning"
        />
        <StatCard
          title={t('analytics.stats.peakTraffic')}
          value={counting?.peak_count || 47}
          subtext={t('analytics.stats.peakAt', { time: '14h30' })}
          icon={Users}
          color="primary"
        />
        <StatCard
          title={t('analytics.stats.alerts')}
          value={dashboard?.alerts?.today || 12}
          change={-5.2}
          icon={AlertTriangle}
          color="danger"
        />
      </div>
      
      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Chart */}
        <div className="bg-dark-800 rounded-2xl p-6">
          <h3 className="font-semibold mb-4">{t('analytics.charts.peopleFlow')}</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={hourlyData}>
                <defs>
                  <linearGradient id="colorEntries" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorExits" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d3848" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: '#1e2530', border: 'none', borderRadius: '8px' }}
                />
                <Area
                  type="monotone"
                  dataKey="entries"
                  stroke="#22c55e"
                  fillOpacity={1}
                  fill="url(#colorEntries)"
                  name={t('analytics.metrics.entries')}
                />
                <Area
                  type="monotone"
                  dataKey="exits"
                  stroke="#f59e0b"
                  fillOpacity={1}
                  fill="url(#colorExits)"
                  name={t('analytics.metrics.exits')}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          
          <div className="flex justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-success" />
              <span className="text-sm text-gray-400">{t('analytics.metrics.entries')}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-warning" />
              <span className="text-sm text-gray-400">{t('analytics.metrics.exits')}</span>
            </div>
          </div>
        </div>
        
        {/* Weekly Comparison */}
        <div className="bg-dark-800 rounded-2xl p-6">
          <h3 className="font-semibold mb-4">{t('analytics.charts.weeklyComparison')}</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d3848" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: '#1e2530', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="entries" fill="#3b82f6" radius={[4, 4, 0, 0]} name={t('analytics.metrics.entries')} />
                <Bar dataKey="exits" fill="#8b5cf6" radius={[4, 4, 0, 0]} name={t('analytics.metrics.exits')} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts by Type */}
        <div className="bg-dark-800 rounded-2xl p-6">
          <h3 className="font-semibold mb-4">{t('analytics.charts.alertsByType')}</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={alertsByType}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {alertsByType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#1e2530', border: 'none', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="space-y-2 mt-4">
            {alertsByType.map((item) => (
              <div key={item.key} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-gray-400">{item.name}</span>
                </div>
                <span className="font-medium">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Peak Hours */}
        <div className="bg-dark-800 rounded-2xl p-6">
          <h3 className="font-semibold mb-4">{t('analytics.charts.peakHours')}</h3>
          
          <div className="space-y-4">
            {[
              { hour: '12h - 14h', value: 85, label: t('analytics.peakHours.lunchBreak') },
              { hour: '17h - 19h', value: 72, label: t('analytics.peakHours.endOfDay') },
              { hour: '9h - 10h', value: 65, label: t('analytics.peakHours.morningArrival') },
              { hour: '14h - 15h', value: 45, label: t('analytics.peakHours.afternoon') },
            ].map((item) => (
              <div key={item.hour}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{item.hour}</span>
                  <span className="text-gray-400">{item.label}</span>
                </div>
                <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.value}%` }}
                    className="h-full bg-gradient-to-r from-primary to-purple rounded-full"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* PPE Compliance */}
        <div className="bg-dark-800 rounded-2xl p-6">
          <h3 className="font-semibold mb-4">{t('analytics.charts.ppeCompliance')}</h3>
          
          <div className="flex items-center justify-center mb-6">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="#2d3848"
                  strokeWidth="12"
                  fill="none"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="#22c55e"
                  strokeWidth="12"
                  fill="none"
                  strokeDasharray={`${87 * 3.51} 351`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-3xl font-bold">87%</span>
                <span className="text-xs text-gray-500">{t('analytics.ppe.statusCompliant')}</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-400">{t('analytics.ppe.helmetsDetected')}</span>
              <span className="text-success">92%</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-400">{t('analytics.ppe.vestsDetected')}</span>
              <span className="text-success">88%</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-400">{t('analytics.ppe.nonCompliances')}</span>
              <span className="text-warning">23</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Heatmap Placeholder */}
      <div className="bg-dark-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">{t('analytics.heatmap.title')}</h3>
          <select className="px-3 py-1.5 bg-dark-700 rounded-lg text-sm">
            <option>{t('analytics.heatmap.periods.today')}</option>
            <option>{t('analytics.heatmap.periods.thisWeek')}</option>
            <option>{t('analytics.heatmap.periods.thisMonth')}</option>
          </select>
        </div>
        
        <div className="aspect-video bg-dark-900 rounded-xl flex items-center justify-center">
          <div className="text-center">
            <BarChart3 size={48} className="mx-auto mb-4 text-gray-600" />
            <p className="text-gray-500">{t('analytics.heatmap.placeholderTitle')}</p>
            <p className="text-xs text-gray-600">{t('analytics.heatmap.placeholderSubtitle')}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, change, subtext, icon: Icon, color }) => {
  const { t } = useTranslation();

  return (
    <div className="bg-dark-800 rounded-2xl p-4">
    <div className="flex items-center justify-between mb-3">
      <span className="text-sm text-gray-400">{title}</span>
      <div className={`w-8 h-8 rounded-lg bg-${color}/20 flex items-center justify-center`}>
        <Icon size={16} className={`text-${color}`} />
      </div>
    </div>
    <p className="text-2xl font-bold mb-1">{value.toLocaleString()}</p>
    {change !== undefined ? (
      <p className={`text-sm flex items-center gap-1 ${change >= 0 ? 'text-success' : 'text-danger'}`}>
        {change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
        {Math.abs(change)}%
        <span className="text-gray-500">{t('analytics.stats.vsPreviousPeriod')}</span>
      </p>
    ) : (
      <p className="text-sm text-gray-500">{subtext}</p>
    )}
  </div>
  );
};

export default Analytics;
