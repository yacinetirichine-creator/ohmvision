/**
 * OhmVision - Settings Page
 * Configuration de l'application
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { User, Bell, Shield, Palette,
  Key, Mail, Smartphone, CreditCard, HelpCircle,
  ChevronRight, Check, Moon, Sun
} from 'lucide-react';
import { useAuthStore } from '../services/store';

const Settings = () => {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('profile');
  
  const tabs = [
    { id: 'profile', label: t('settings.tabs.profile'), icon: User },
    { id: 'notifications', label: t('settings.tabs.notifications'), icon: Bell },
    { id: 'security', label: t('settings.tabs.security'), icon: Shield },
    { id: 'appearance', label: t('settings.tabs.appearance'), icon: Palette },
    { id: 'billing', label: t('settings.tabs.billing'), icon: CreditCard },
    { id: 'help', label: t('settings.tabs.help'), icon: HelpCircle },
  ];
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">{t('settings.title')}</h1>
        <p className="text-gray-500">{t('settings.subtitle')}</p>
      </div>
      
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Tabs Navigation */}
        <div className="lg:w-64 flex-shrink-0">
          <div className="bg-dark-800 rounded-2xl p-2 flex lg:flex-col gap-1 overflow-x-auto lg:overflow-visible">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl whitespace-nowrap
                  transition-all flex-shrink-0 lg:flex-shrink lg:w-full
                  ${activeTab === tab.id
                    ? 'bg-primary text-white'
                    : 'text-gray-400 hover:bg-dark-700 hover:text-white'
                  }
                `}
              >
                <tab.icon size={18} />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1">
          <div className="bg-dark-800 rounded-2xl p-6">
            {activeTab === 'profile' && <ProfileSettings user={user} />}
            {activeTab === 'notifications' && <NotificationSettings />}
            {activeTab === 'security' && <SecuritySettings />}
            {activeTab === 'appearance' && <AppearanceSettings />}
            {activeTab === 'billing' && <BillingSettings />}
            {activeTab === 'help' && <HelpSection />}
          </div>
        </div>
      </div>
    </div>
  );
};

// Profile Settings
const ProfileSettings = ({ user }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: ''
  });
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t('settings.profile.title')}</h2>
        <p className="text-gray-500 text-sm">{t('settings.profile.subtitle')}</p>
      </div>
      
      {/* Avatar */}
      <div className="flex items-center gap-4">
        <div className="w-20 h-20 bg-gradient-to-br from-primary to-purple rounded-full flex items-center justify-center text-2xl font-bold">
          {formData.first_name?.[0] || formData.email?.[0]?.toUpperCase() || 'U'}
        </div>
        <div>
          <button className="px-4 py-2 bg-primary hover:bg-primary-dark rounded-lg text-sm">
            {t('settings.profile.changePhoto')}
          </button>
          <p className="text-xs text-gray-500 mt-1">{t('settings.profile.photoHint')}</p>
        </div>
      </div>
      
      {/* Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-gray-400 mb-2">{t('settings.profile.fields.firstName')}</label>
          <input
            type="text"
            value={formData.first_name}
            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
            className="w-full px-4 py-3 bg-dark-700 border border-dark-500 rounded-xl focus:outline-none focus:border-primary"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-2">{t('settings.profile.fields.lastName')}</label>
          <input
            type="text"
            value={formData.last_name}
            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
            className="w-full px-4 py-3 bg-dark-700 border border-dark-500 rounded-xl focus:outline-none focus:border-primary"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-2">{t('settings.profile.fields.email')}</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-4 py-3 bg-dark-700 border border-dark-500 rounded-xl focus:outline-none focus:border-primary"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-2">{t('settings.profile.fields.phone')}</label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            placeholder={t('settings.profile.placeholders.phone')}
            className="w-full px-4 py-3 bg-dark-700 border border-dark-500 rounded-xl focus:outline-none focus:border-primary"
          />
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="px-6 py-2.5 bg-primary hover:bg-primary-dark rounded-xl">
          {t('settings.profile.save')}
        </button>
      </div>
    </div>
  );
};

// Notification Settings
const NotificationSettings = () => {
  const { t } = useTranslation();
  const [settings, setSettings] = useState({
    email_alerts: true,
    sms_alerts: false,
    push_alerts: true,
    alert_critical: true,
    alert_high: true,
    alert_medium: false,
    alert_low: false,
    daily_report: true,
    weekly_report: true
  });
  
  const Toggle = ({ enabled, onChange }) => (
    <button
      onClick={() => onChange(!enabled)}
      className={`w-12 h-6 rounded-full transition-colors ${enabled ? 'bg-primary' : 'bg-dark-600'}`}
    >
      <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
    </button>
  );
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t('settings.notifications.title')}</h2>
        <p className="text-gray-500 text-sm">{t('settings.notifications.subtitle')}</p>
      </div>
      
      {/* Channels */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.notifications.channels.title')}</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail size={20} className="text-gray-400" />
              <div>
                <p className="font-medium">{t('settings.notifications.channels.email.title')}</p>
                <p className="text-sm text-gray-500">{t('settings.notifications.channels.email.subtitle')}</p>
              </div>
            </div>
            <Toggle enabled={settings.email_alerts} onChange={(v) => setSettings({ ...settings, email_alerts: v })} />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Smartphone size={20} className="text-gray-400" />
              <div>
                <p className="font-medium">{t('settings.notifications.channels.sms.title')}</p>
                <p className="text-sm text-gray-500">{t('settings.notifications.channels.sms.subtitle')}</p>
              </div>
            </div>
            <Toggle enabled={settings.sms_alerts} onChange={(v) => setSettings({ ...settings, sms_alerts: v })} />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell size={20} className="text-gray-400" />
              <div>
                <p className="font-medium">{t('settings.notifications.channels.push.title')}</p>
                <p className="text-sm text-gray-500">{t('settings.notifications.channels.push.subtitle')}</p>
              </div>
            </div>
            <Toggle enabled={settings.push_alerts} onChange={(v) => setSettings({ ...settings, push_alerts: v })} />
          </div>
        </div>
      </div>
      
      {/* Severity Levels */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.notifications.severity.title')}</h3>
        <div className="space-y-3">
          {[
            { key: 'alert_critical', label: t('settings.notifications.severity.levels.critical'), color: 'danger' },
            { key: 'alert_high', label: t('settings.notifications.severity.levels.high'), color: 'warning' },
            { key: 'alert_medium', label: t('settings.notifications.severity.levels.medium'), color: 'primary' },
            { key: 'alert_low', label: t('settings.notifications.severity.levels.low'), color: 'gray-400' },
          ].map((level) => (
            <div key={level.key} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`w-3 h-3 rounded-full bg-${level.color}`} />
                <span>{level.label}</span>
              </div>
              <Toggle enabled={settings[level.key]} onChange={(v) => setSettings({ ...settings, [level.key]: v })} />
            </div>
          ))}
        </div>
      </div>
      
      {/* Reports */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.notifications.reports.title')}</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span>{t('settings.notifications.reports.daily')}</span>
            <Toggle enabled={settings.daily_report} onChange={(v) => setSettings({ ...settings, daily_report: v })} />
          </div>
          <div className="flex items-center justify-between">
            <span>{t('settings.notifications.reports.weekly')}</span>
            <Toggle enabled={settings.weekly_report} onChange={(v) => setSettings({ ...settings, weekly_report: v })} />
          </div>
        </div>
      </div>
    </div>
  );
};

// Security Settings
const SecuritySettings = () => {
  const { t } = useTranslation();
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t('settings.security.title')}</h2>
        <p className="text-gray-500 text-sm">{t('settings.security.subtitle')}</p>
      </div>
      
      {/* Password */}
      <div className="p-4 bg-dark-700 rounded-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Key size={20} className="text-gray-400" />
            <div>
              <p className="font-medium">{t('settings.security.password.title')}</p>
              <p className="text-sm text-gray-500">{t('settings.security.password.lastChanged')}</p>
            </div>
          </div>
          <button className="px-4 py-2 bg-dark-600 hover:bg-dark-500 rounded-lg text-sm">
            {t('settings.security.password.edit')}
          </button>
        </div>
      </div>
      
      {/* 2FA */}
      <div className="p-4 bg-dark-700 rounded-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield size={20} className="text-gray-400" />
            <div>
              <p className="font-medium">{t('settings.security.twoFactor.title')}</p>
              <p className="text-sm text-gray-500">{t('settings.security.twoFactor.subtitle')}</p>
            </div>
          </div>
          <button className="px-4 py-2 bg-primary hover:bg-primary-dark rounded-lg text-sm">
            {t('settings.security.twoFactor.enable')}
          </button>
        </div>
      </div>
      
      {/* Sessions */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.security.sessions.title')}</h3>
        <div className="space-y-3">
          {[
            { device: 'Chrome - Windows', location: 'Paris, France', current: true },
            { device: 'Safari - iPhone', location: 'Paris, France', current: false },
          ].map((session, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-dark-700 rounded-xl">
              <div>
                <p className="font-medium flex items-center gap-2">
                  {session.device}
                  {session.current && (
                    <span className="text-xs bg-success/20 text-success px-2 py-0.5 rounded">
                      {t('settings.security.sessions.current')}
                    </span>
                  )}
                </p>
                <p className="text-sm text-gray-500">{session.location}</p>
              </div>
              {!session.current && (
                <button className="text-sm text-danger hover:text-danger/80">
                  {t('settings.security.sessions.disconnect')}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Appearance Settings
const AppearanceSettings = () => {
  const { t, i18n } = useTranslation();
  const [theme, setTheme] = useState('dark');
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t('settings.appearance.title')}</h2>
        <p className="text-gray-500 text-sm">{t('settings.appearance.subtitle')}</p>
      </div>
      
      {/* Theme */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.appearance.theme.title')}</h3>
        <div className="flex gap-3">
          {[
            { id: 'dark', label: t('settings.appearance.theme.dark'), icon: Moon },
            { id: 'light', label: t('settings.appearance.theme.light'), icon: Sun },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTheme(t.id)}
              className={`
                flex-1 p-4 rounded-xl border-2 flex items-center justify-center gap-3
                ${theme === t.id ? 'border-primary bg-primary/10' : 'border-dark-500 hover:border-dark-400'}
              `}
            >
              <t.icon size={20} />
              <span>{t.label}</span>
              {theme === t.id && <Check size={18} className="text-primary" />}
            </button>
          ))}
        </div>
      </div>
      
      {/* Language */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.appearance.language.title')}</h3>
        <select
          value={i18n.resolvedLanguage || i18n.language || 'fr'}
          onChange={(e) => i18n.changeLanguage(e.target.value)}
          className="w-full px-4 py-3 bg-dark-700 border border-dark-500 rounded-xl focus:outline-none focus:border-primary"
        >
          <option value="fr">{t('common.languages.fr')}</option>
          <option value="en">{t('common.languages.en')}</option>
          <option value="es">{t('common.languages.es')}</option>
        </select>
      </div>
    </div>
  );
};

// Billing Settings
const BillingSettings = () => {
  const { t } = useTranslation();
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t('settings.billing.title')}</h2>
        <p className="text-gray-500 text-sm">{t('settings.billing.subtitle')}</p>
      </div>
      
      {/* Current Plan */}
      <div className="p-6 bg-gradient-to-br from-primary/20 to-purple/20 rounded-2xl border border-primary/30">
        <div className="flex items-center justify-between mb-4">
          <div>
            <span className="text-sm text-gray-400">{t('settings.billing.currentPlan.label')}</span>
            <h3 className="text-2xl font-bold">Business</h3>
          </div>
          <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
            {t('common.active')}
          </span>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-400">{t('settings.billing.currentPlan.price')}</p>
            <p className="font-semibold">149€/mois</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">{t('settings.billing.currentPlan.nextPayment')}</p>
            <p className="font-semibold">15 janvier 2025</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">{t('settings.billing.currentPlan.cameras')}</p>
            <p className="font-semibold">8 / 20</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">{t('settings.billing.currentPlan.users')}</p>
            <p className="font-semibold">3 / 5</p>
          </div>
        </div>
        
        <button className="w-full py-2.5 bg-primary hover:bg-primary-dark rounded-xl">
          {t('settings.billing.currentPlan.change')}
        </button>
      </div>
      
      {/* Payment Method */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.billing.paymentMethod.title')}</h3>
        <div className="p-4 bg-dark-700 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-7 bg-gradient-to-r from-blue-600 to-blue-400 rounded flex items-center justify-center text-white text-xs font-bold">
              VISA
            </div>
            <div>
              <p className="font-medium">•••• •••• •••• 4242</p>
              <p className="text-sm text-gray-500">{t('settings.billing.paymentMethod.expires', { date: '12/26' })}</p>
            </div>
          </div>
          <button className="text-sm text-primary">{t('settings.billing.paymentMethod.edit')}</button>
        </div>
      </div>
      
      {/* Invoices */}
      <div>
        <h3 className="font-medium mb-4">{t('settings.billing.invoices.title')}</h3>
        <div className="space-y-2">
          {[
            { date: 'Déc 2024', amount: '149,00 €', status: 'Payée' },
            { date: 'Nov 2024', amount: '149,00 €', status: 'Payée' },
            { date: 'Oct 2024', amount: '149,00 €', status: 'Payée' },
          ].map((invoice, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-dark-700 rounded-xl">
              <div>
                <p className="font-medium">{invoice.date}</p>
                <p className="text-sm text-success">{invoice.status}</p>
              </div>
              <div className="flex items-center gap-4">
                <span className="font-medium">{invoice.amount}</span>
                <button className="text-sm text-primary">{t('settings.billing.invoices.download')}</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Help Section
const HelpSection = () => {
  const { t } = useTranslation();
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">{t('settings.help.title')}</h2>
        <p className="text-gray-500 text-sm">{t('settings.help.subtitle')}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { title: t('settings.help.cards.documentation.title'), desc: t('settings.help.cards.documentation.desc'), icon: '📚' },
          { title: t('settings.help.cards.faq.title'), desc: t('settings.help.cards.faq.desc'), icon: '❓' },
          { title: t('settings.help.cards.support.title'), desc: t('settings.help.cards.support.desc'), icon: '💬' },
          { title: t('settings.help.cards.status.title'), desc: t('settings.help.cards.status.desc'), icon: '🟢' },
        ].map((item, index) => (
          <button
            key={index}
            className="p-4 bg-dark-700 hover:bg-dark-600 rounded-xl text-left flex items-center gap-4"
          >
            <span className="text-2xl">{item.icon}</span>
            <div className="flex-1">
              <p className="font-medium">{item.title}</p>
              <p className="text-sm text-gray-500">{item.desc}</p>
            </div>
            <ChevronRight size={18} className="text-gray-600" />
          </button>
        ))}
      </div>
      
      <div className="p-4 bg-dark-700 rounded-xl">
        <p className="text-sm text-gray-400 mb-2">{t('settings.help.appVersion')}</p>
        <p className="font-mono">OhmVision v1.0.0</p>
      </div>
    </div>
  );
};

export default Settings;
