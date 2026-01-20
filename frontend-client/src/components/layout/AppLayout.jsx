/**
 * OhmVision - App Layout (Mobile/Tablet/Desktop)
 */

import React, { useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard, Camera, Bell, BarChart3, Settings,
  Bot, Menu, X, LogOut, User, Crown, MessageSquare
} from 'lucide-react';
import { useAuthStore, useAlertsStore, useUIStore } from '../../services/store';
import LanguageSwitcher from '../LanguageSwitcher';

const AppLayout = () => {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { unreadCount, fetchAlerts } = useAlertsStore();
  const { sidebarOpen, toggleSidebar, closeSidebar } = useUIStore();
  const { t } = useTranslation();
  
  useEffect(() => {
    fetchAlerts({ limit: 50 });
    const interval = setInterval(() => fetchAlerts({ limit: 50 }), 30000);
    return () => clearInterval(interval);
  }, [fetchAlerts]);
  
  useEffect(() => { closeSidebar(); }, [closeSidebar, location.pathname]);
  
  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: t('nav.dashboard') },
    { path: '/executive', icon: Crown, label: t('nav.executive') },
    { path: '/cameras', icon: Camera, label: t('nav.cameras') },
    { path: '/alerts', icon: Bell, label: t('nav.alerts'), badge: unreadCount },
    { path: '/analytics', icon: BarChart3, label: t('nav.analytics') },
    { path: '/ai', icon: Bot, label: t('nav.aiAssistant') },
    { path: '/notifications', icon: MessageSquare, label: t('nav.notifications') },
    { path: '/settings', icon: Settings, label: t('nav.settings') },
  ];
  
  return (
    <div className="flex h-full bg-dark-900">
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={closeSidebar}
          />
        )}
      </AnimatePresence>
      
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-dark-800 border-r border-dark-500
        transform transition-transform duration-300
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        flex flex-col safe-area-top
      `}>
        <div className="flex items-center justify-between p-4 border-b border-dark-500">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-purple rounded-xl flex items-center justify-center">
              <span className="text-xl">👁️</span>
            </div>
            <div>
              <h1 className="font-bold text-lg">{t('common.brand')}</h1>
              <span className="text-xs text-gray-500">v1.0.0</span>
            </div>
          </div>
          <div className="hidden lg:block">
            <LanguageSwitcher />
          </div>
          <button onClick={closeSidebar} className="lg:hidden p-2 hover:bg-dark-700 rounded-lg">
            <X size={20} />
          </button>
        </div>
        
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-xl transition-all
                ${isActive 
                  ? 'bg-primary/10 text-primary border-l-4 border-primary' 
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white border-l-4 border-transparent'}
              `}
            >
              <item.icon size={20} />
              <span className="font-medium">{item.label}</span>
              {item.badge > 0 && (
                <span className="ml-auto bg-danger text-white text-xs px-2 py-0.5 rounded-full">
                  {item.badge > 99 ? '99+' : item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
        
        <div className="p-4 border-t border-dark-500">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-dark-700">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-purple rounded-full flex items-center justify-center">
              <User size={18} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{user?.first_name || user?.email?.split('@')[0]}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
            <button onClick={logout} className="p-2 hover:bg-dark-600 rounded-lg text-gray-400 hover:text-danger">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>
      
      <main className="flex-1 flex flex-col min-w-0 h-full">
        <header className="lg:hidden flex items-center justify-between p-4 bg-dark-800 border-b border-dark-500">
          <button onClick={toggleSidebar} className="p-2 hover:bg-dark-700 rounded-lg">
            <Menu size={24} />
          </button>
          <div className="flex items-center gap-2">
            <span className="text-xl">👁️</span>
            <span className="font-bold">{t('common.brand')}</span>
          </div>
          <div className="flex items-center gap-2">
            <LanguageSwitcher className="sm:mr-1" />
            <NavLink to="/alerts" className="relative p-2 hover:bg-dark-700 rounded-lg">
              <Bell size={24} />
              {unreadCount > 0 && <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full" />}
            </NavLink>
          </div>
        </header>
        
        <div className="flex-1 overflow-y-auto p-4 lg:p-6 safe-area-bottom">
          <Outlet />
        </div>
        
        <nav className="lg:hidden flex items-center justify-around p-2 bg-dark-800 border-t border-dark-500">
          {navItems.slice(0, 5).map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `flex flex-col items-center gap-1 p-2 rounded-lg min-w-[60px] ${isActive ? 'text-primary' : 'text-gray-500'}`}
            >
              <div className="relative">
                <item.icon size={22} />
                {item.badge > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-danger text-white text-[10px] rounded-full flex items-center justify-center">
                    {item.badge > 9 ? '9+' : item.badge}
                  </span>
                )}
              </div>
              <span className="text-[10px]">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </main>
    </div>
  );
};

export default AppLayout;
