/**
 * OhmVision - RealTimeStats
 * Statistiques temps réel avec graphiques animés et design glassmorphism
 */

import React, { useState, useEffect } from 'react';
import {
  Users, Car, Flame, HardHat, AlertTriangle, TrendingUp,
  TrendingDown, Activity, Clock, Shield, Eye, Zap,
  ThermometerSun, Wind, Camera, Bell
} from 'lucide-react';

// Mini sparkline chart component
const Sparkline = ({ data, color = '#6366f1', height = 40 }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = height - ((val - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg className="w-full" height={height} preserveAspectRatio="none">
      <defs>
        <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polygon
        points={`0,${height} ${points} 100,${height}`}
        fill={`url(#gradient-${color})`}
      />
    </svg>
  );
};

// Stat card with glassmorphism
const StatCard = ({ 
  icon: Icon, 
  label, 
  value, 
  trend, 
  trendValue,
  color = 'primary',
  sparklineData,
  unit = '',
  animate = true 
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  
  // Animate counter
  useEffect(() => {
    if (!animate) {
      setDisplayValue(value);
      return;
    }
    
    const duration = 500;
    const steps = 20;
    const increment = (value - displayValue) / steps;
    let current = displayValue;
    let step = 0;
    
    const timer = setInterval(() => {
      step++;
      current += increment;
      setDisplayValue(Math.round(current));
      
      if (step >= steps) {
        setDisplayValue(value);
        clearInterval(timer);
      }
    }, duration / steps);
    
    return () => clearInterval(timer);
  }, [value]);

  const colorClasses = {
    primary: 'from-indigo-500/20 to-purple-500/20 border-indigo-500/30',
    green: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
    orange: 'from-orange-500/20 to-amber-500/20 border-orange-500/30',
    red: 'from-red-500/20 to-pink-500/20 border-red-500/30',
    purple: 'from-purple-500/20 to-fuchsia-500/20 border-purple-500/30',
  };

  const iconColors = {
    primary: 'text-indigo-400',
    green: 'text-green-400',
    blue: 'text-blue-400',
    orange: 'text-orange-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
  };

  const sparklineColors = {
    primary: '#818cf8',
    green: '#4ade80',
    blue: '#60a5fa',
    orange: '#fb923c',
    red: '#f87171',
    purple: '#c084fc',
  };

  return (
    <div className={`
      relative overflow-hidden rounded-2xl p-4
      bg-gradient-to-br ${colorClasses[color]}
      border backdrop-blur-xl
      transition-all duration-300 hover:scale-[1.02] hover:shadow-lg
    `}>
      {/* Background glow effect */}
      <div className={`
        absolute -top-10 -right-10 w-32 h-32 rounded-full
        bg-gradient-to-br ${colorClasses[color]} blur-3xl opacity-50
      `} />
      
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-3">
          <div className={`p-2 rounded-xl bg-white/10 ${iconColors[color]}`}>
            <Icon size={20} />
          </div>
          
          {trend && (
            <div className={`
              flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium
              ${trend === 'up' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}
            `}>
              {trend === 'up' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
              {trendValue}
            </div>
          )}
        </div>
        
        <div className="mb-2">
          <p className="text-2xl font-bold text-white">
            {displayValue.toLocaleString()}{unit}
          </p>
          <p className="text-sm text-gray-400">{label}</p>
        </div>
        
        {sparklineData && (
          <div className="mt-3 -mx-1">
            <Sparkline data={sparklineData} color={sparklineColors[color]} height={30} />
          </div>
        )}
      </div>
    </div>
  );
};

// Alert ticker component
const AlertTicker = ({ alerts }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  useEffect(() => {
    if (alerts.length <= 1) return;
    
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % alerts.length);
    }, 4000);
    
    return () => clearInterval(timer);
  }, [alerts.length]);

  if (alerts.length === 0) return null;

  const currentAlert = alerts[currentIndex];
  
  const alertColors = {
    critical: 'bg-red-500/20 border-red-500/50 text-red-400',
    warning: 'bg-orange-500/20 border-orange-500/50 text-orange-400',
    info: 'bg-blue-500/20 border-blue-500/50 text-blue-400',
  };

  return (
    <div className={`
      flex items-center gap-3 p-3 rounded-xl border
      ${alertColors[currentAlert.severity]}
      transition-all duration-500
    `}>
      <AlertTriangle size={18} className="animate-pulse" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{currentAlert.message}</p>
        <p className="text-xs opacity-70">{currentAlert.camera} • {currentAlert.time}</p>
      </div>
      <div className="flex items-center gap-1 text-xs opacity-70">
        <span>{currentIndex + 1}/{alerts.length}</span>
      </div>
    </div>
  );
};

// Live activity indicator
const LiveActivity = ({ events }) => {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Activity size={16} className="text-primary" />
          Activité en direct
        </h3>
        <div className="flex items-center gap-1 text-xs text-green-400">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          Live
        </div>
      </div>
      
      <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
        {events.map((event, index) => (
          <div 
            key={index}
            className={`
              flex items-center gap-3 p-2 rounded-lg bg-dark-700/50
              animate-slideIn
            `}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className={`
              w-8 h-8 rounded-lg flex items-center justify-center
              ${event.type === 'person' ? 'bg-green-500/20 text-green-400' :
                event.type === 'vehicle' ? 'bg-blue-500/20 text-blue-400' :
                event.type === 'alert' ? 'bg-red-500/20 text-red-400' :
                'bg-gray-500/20 text-gray-400'}
            `}>
              {event.type === 'person' ? <Users size={14} /> :
               event.type === 'vehicle' ? <Car size={14} /> :
               event.type === 'alert' ? <AlertTriangle size={14} /> :
               <Eye size={14} />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-white truncate">{event.message}</p>
              <p className="text-xs text-gray-500">{event.camera}</p>
            </div>
            <span className="text-xs text-gray-500">{event.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main RealTimeStats component
const RealTimeStats = () => {
  const [stats, setStats] = useState({
    totalPersons: 47,
    totalVehicles: 12,
    activeAlerts: 3,
    ppeCompliance: 94,
    temperature: 23,
    camerasOnline: 16,
  });
  
  const [sparklines, setSparklines] = useState({
    persons: [30, 35, 42, 38, 45, 40, 47],
    vehicles: [8, 10, 9, 12, 11, 10, 12],
    alerts: [5, 3, 4, 2, 3, 4, 3],
    compliance: [91, 92, 93, 92, 94, 93, 94],
  });
  
  const [alerts, setAlerts] = useState([
    { severity: 'critical', message: 'Intrusion zone restreinte', camera: 'Entrée Nord', time: 'Il y a 2 min' },
    { severity: 'warning', message: 'EPI non conforme détecté', camera: 'Atelier B', time: 'Il y a 5 min' },
    { severity: 'info', message: 'File d\'attente > 5 personnes', camera: 'Accueil', time: 'Il y a 8 min' },
  ]);
  
  const [events, setEvents] = useState([
    { type: 'person', message: 'Nouvelle personne détectée', camera: 'Hall principal', time: '10:45' },
    { type: 'vehicle', message: 'Véhicule entré parking', camera: 'Parking A', time: '10:43' },
    { type: 'alert', message: 'Mouvement zone interdite', camera: 'Entrepôt', time: '10:40' },
    { type: 'person', message: '3 personnes comptées', camera: 'Sortie Sud', time: '10:38' },
  ]);
  
  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        totalPersons: prev.totalPersons + Math.floor(Math.random() * 5) - 2,
        totalVehicles: prev.totalVehicles + Math.floor(Math.random() * 3) - 1,
        activeAlerts: Math.max(0, prev.activeAlerts + Math.floor(Math.random() * 3) - 1),
        ppeCompliance: Math.min(100, Math.max(85, prev.ppeCompliance + Math.floor(Math.random() * 3) - 1)),
        temperature: prev.temperature + (Math.random() - 0.5) * 2,
        camerasOnline: prev.camerasOnline,
      }));
      
      setSparklines(prev => ({
        persons: [...prev.persons.slice(1), stats.totalPersons],
        vehicles: [...prev.vehicles.slice(1), stats.totalVehicles],
        alerts: [...prev.alerts.slice(1), stats.activeAlerts],
        compliance: [...prev.compliance.slice(1), stats.ppeCompliance],
      }));
    }, 3000);
    
    return () => clearInterval(interval);
  }, [stats]);

  return (
    <div className="space-y-6">
      {/* Alert ticker */}
      <AlertTicker alerts={alerts} />
      
      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard
          icon={Users}
          label="Personnes détectées"
          value={stats.totalPersons}
          trend="up"
          trendValue="+12%"
          color="green"
          sparklineData={sparklines.persons}
        />
        
        <StatCard
          icon={Car}
          label="Véhicules"
          value={stats.totalVehicles}
          trend="up"
          trendValue="+5%"
          color="blue"
          sparklineData={sparklines.vehicles}
        />
        
        <StatCard
          icon={AlertTriangle}
          label="Alertes actives"
          value={stats.activeAlerts}
          trend="down"
          trendValue="-23%"
          color="red"
          sparklineData={sparklines.alerts}
        />
        
        <StatCard
          icon={HardHat}
          label="Conformité EPI"
          value={stats.ppeCompliance}
          unit="%"
          trend="up"
          trendValue="+2%"
          color="orange"
          sparklineData={sparklines.compliance}
        />
        
        <StatCard
          icon={ThermometerSun}
          label="Température"
          value={Math.round(stats.temperature)}
          unit="°C"
          color="purple"
        />
        
        <StatCard
          icon={Camera}
          label="Caméras en ligne"
          value={stats.camerasOnline}
          unit="/16"
          color="primary"
        />
      </div>
      
      {/* Live activity */}
      <div className="p-4 rounded-2xl bg-dark-800/50 backdrop-blur-xl border border-dark-700">
        <LiveActivity events={events} />
      </div>
    </div>
  );
};

export default RealTimeStats;

// Custom scrollbar styles (add to index.css)
const styles = `
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.2);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
.animate-slideIn {
  animation: slideIn 0.3s ease-out forwards;
}
`;
