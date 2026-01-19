/**
 * OhmVision - Notifications Configuration Page
 * Configuration des canaux de notification multi-canal
 */

import React, { useState, useEffect } from 'react';
import {
  Mail, MessageCircle, Send, Webhook, Bell, Smartphone,
  Plus, Trash2, Save, TestTube, Check, X, AlertCircle,
  Settings, ChevronDown, ChevronUp
} from 'lucide-react';

const CHANNELS = [
  { id: 'email', name: 'Email', icon: Mail, color: 'blue' },
  { id: 'telegram', name: 'Telegram', icon: Send, color: 'sky' },
  { id: 'discord', name: 'Discord', icon: MessageCircle, color: 'indigo' },
  { id: 'sms', name: 'SMS', icon: Smartphone, color: 'green' },
  { id: 'slack', name: 'Slack', icon: MessageCircle, color: 'purple' },
  { id: 'teams', name: 'Microsoft Teams', icon: MessageCircle, color: 'blue' },
  { id: 'webhook', name: 'Webhook', icon: Webhook, color: 'gray' }
];

const SEVERITY_LEVELS = [
  { id: 'info', name: 'Info', color: 'blue' },
  { id: 'warning', name: 'Avertissement', color: 'yellow' },
  { id: 'high', name: 'Élevé', color: 'orange' },
  { id: 'critical', name: 'Critique', color: 'red' }
];

const ALERT_TYPES = [
  { id: 'fall', name: 'Chute' },
  { id: 'fire', name: 'Feu/Fumée' },
  { id: 'intrusion', name: 'Intrusion' },
  { id: 'ppe_violation', name: 'Non-conformité EPI' },
  { id: 'crowd', name: 'Formation de foule' },
  { id: 'loitering', name: 'Flânerie' },
  { id: 'running', name: 'Course' },
  { id: 'fighting', name: 'Bagarre' }
];

const NotificationsConfig = () => {
  const [channels, setChannels] = useState([]);
  const [showAddChannel, setShowAddChannel] = useState(false);
  const [newChannel, setNewChannel] = useState({
    name: '',
    channel: 'email',
    enabled: true,
    config: {},
    min_severity: 'warning',
    alert_types: []
  });
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedChannel, setExpandedChannel] = useState(null);

  useEffect(() => {
    fetchChannels();
  }, []);

  const fetchChannels = async () => {
    try {
      const response = await fetch('/api/advanced/notifications/channels');
      const data = await response.json();
      setChannels(data.channels || []);
    } catch (err) {
      console.error('Error fetching channels:', err);
    }
  };

  const addChannel = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/advanced/notifications/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newChannel)
      });
      
      if (response.ok) {
        await fetchChannels();
        setShowAddChannel(false);
        setNewChannel({
          name: '',
          channel: 'email',
          enabled: true,
          config: {},
          min_severity: 'warning',
          alert_types: []
        });
      }
    } catch (err) {
      console.error('Error adding channel:', err);
    }
    setLoading(false);
  };

  const deleteChannel = async (name) => {
    if (!confirm(`Supprimer le canal "${name}" ?`)) return;
    
    try {
      await fetch(`/api/advanced/notifications/channels/${name}`, {
        method: 'DELETE'
      });
      await fetchChannels();
    } catch (err) {
      console.error('Error deleting channel:', err);
    }
  };

  const testChannel = async (channelName) => {
    setTestResult({ channel: channelName, status: 'testing' });
    
    try {
      const response = await fetch('/api/advanced/notifications/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel_name: channelName,
          message: '🧪 Test notification from OhmVision'
        })
      });
      
      const data = await response.json();
      setTestResult({
        channel: channelName,
        status: data.results?.[channelName] ? 'success' : 'failed'
      });
      
      setTimeout(() => setTestResult(null), 3000);
    } catch (err) {
      setTestResult({ channel: channelName, status: 'failed' });
    }
  };

  const getChannelIcon = (channelId) => {
    const channel = CHANNELS.find(c => c.id === channelId);
    return channel?.icon || Bell;
  };

  const getChannelColor = (channelId) => {
    const channel = CHANNELS.find(c => c.id === channelId);
    return channel?.color || 'gray';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configuration des Notifications</h1>
          <p className="text-gray-500">Gérez vos canaux de notification multi-canal</p>
        </div>
        
        <button
          onClick={() => setShowAddChannel(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          <Plus size={18} />
          Ajouter un canal
        </button>
      </div>

      {/* Liste des canaux */}
      <div className="space-y-4">
        {channels.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl">
            <Bell size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">Aucun canal de notification configuré</p>
            <button
              onClick={() => setShowAddChannel(true)}
              className="mt-4 text-purple-600 hover:underline"
            >
              Ajouter votre premier canal
            </button>
          </div>
        ) : (
          channels.map((channel) => {
            const Icon = getChannelIcon(channel.channel);
            const color = getChannelColor(channel.channel);
            const isExpanded = expandedChannel === channel.name;
            
            return (
              <div key={channel.name} className="bg-white rounded-xl shadow-sm overflow-hidden">
                <div className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-lg bg-${color}-100`}>
                      <Icon size={24} className={`text-${color}-600`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{channel.name}</h3>
                      <p className="text-sm text-gray-500">
                        {CHANNELS.find(c => c.id === channel.channel)?.name} • 
                        Min: {SEVERITY_LEVELS.find(s => s.id === channel.min_severity)?.name}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    {/* Status */}
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      channel.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                    }`}>
                      {channel.enabled ? 'Actif' : 'Inactif'}
                    </span>
                    
                    {/* Test */}
                    <button
                      onClick={() => testChannel(channel.name)}
                      disabled={testResult?.channel === channel.name && testResult?.status === 'testing'}
                      className="p-2 hover:bg-gray-100 rounded-lg"
                      title="Tester"
                    >
                      {testResult?.channel === channel.name ? (
                        testResult.status === 'testing' ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-2 border-purple-600 border-t-transparent" />
                        ) : testResult.status === 'success' ? (
                          <Check size={20} className="text-green-600" />
                        ) : (
                          <X size={20} className="text-red-600" />
                        )
                      ) : (
                        <TestTube size={20} className="text-gray-400" />
                      )}
                    </button>
                    
                    {/* Delete */}
                    <button
                      onClick={() => deleteChannel(channel.name)}
                      className="p-2 hover:bg-red-50 rounded-lg text-gray-400 hover:text-red-600"
                      title="Supprimer"
                    >
                      <Trash2 size={20} />
                    </button>
                    
                    {/* Expand */}
                    <button
                      onClick={() => setExpandedChannel(isExpanded ? null : channel.name)}
                      className="p-2 hover:bg-gray-100 rounded-lg"
                    >
                      {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </button>
                  </div>
                </div>
                
                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-4 pb-4 border-t bg-gray-50">
                    <p className="py-3 text-sm text-gray-500">
                      Configuration détaillée du canal...
                    </p>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Modal Ajouter Canal */}
      {showAddChannel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">Ajouter un Canal de Notification</h2>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Nom */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom du canal
                </label>
                <input
                  type="text"
                  value={newChannel.name}
                  onChange={(e) => setNewChannel({...newChannel, name: e.target.value})}
                  placeholder="Ex: Alertes Telegram"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              
              {/* Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type de canal
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {CHANNELS.map((ch) => {
                    const Icon = ch.icon;
                    return (
                      <button
                        key={ch.id}
                        onClick={() => setNewChannel({...newChannel, channel: ch.id})}
                        className={`p-3 rounded-lg border-2 flex flex-col items-center gap-1 ${
                          newChannel.channel === ch.id
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <Icon size={20} />
                        <span className="text-xs">{ch.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
              
              {/* Configuration spécifique */}
              {newChannel.channel === 'email' && (
                <EmailConfig config={newChannel.config} onChange={(c) => setNewChannel({...newChannel, config: c})} />
              )}
              {newChannel.channel === 'telegram' && (
                <TelegramConfig config={newChannel.config} onChange={(c) => setNewChannel({...newChannel, config: c})} />
              )}
              {newChannel.channel === 'discord' && (
                <DiscordConfig config={newChannel.config} onChange={(c) => setNewChannel({...newChannel, config: c})} />
              )}
              {newChannel.channel === 'webhook' && (
                <WebhookConfig config={newChannel.config} onChange={(c) => setNewChannel({...newChannel, config: c})} />
              )}
              
              {/* Sévérité minimum */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sévérité minimum
                </label>
                <select
                  value={newChannel.min_severity}
                  onChange={(e) => setNewChannel({...newChannel, min_severity: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  {SEVERITY_LEVELS.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
              
              {/* Types d'alertes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Types d'alertes (laisser vide pour tous)
                </label>
                <div className="flex flex-wrap gap-2">
                  {ALERT_TYPES.map((type) => (
                    <button
                      key={type.id}
                      onClick={() => {
                        const types = newChannel.alert_types || [];
                        const newTypes = types.includes(type.id)
                          ? types.filter(t => t !== type.id)
                          : [...types, type.id];
                        setNewChannel({...newChannel, alert_types: newTypes});
                      }}
                      className={`px-3 py-1 rounded-full text-sm ${
                        (newChannel.alert_types || []).includes(type.id)
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="p-6 border-t flex justify-end gap-3">
              <button
                onClick={() => setShowAddChannel(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={addChannel}
                disabled={!newChannel.name || loading}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                {loading ? 'Ajout...' : 'Ajouter'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Configuration spécifique par canal

const EmailConfig = ({ config, onChange }) => (
  <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
    <input
      type="email"
      placeholder="Email destinataire"
      value={config.to_email || ''}
      onChange={(e) => onChange({...config, to_email: e.target.value})}
      className="w-full px-3 py-2 border rounded-lg"
    />
    <input
      type="text"
      placeholder="Serveur SMTP (ex: smtp.gmail.com)"
      value={config.smtp_host || ''}
      onChange={(e) => onChange({...config, smtp_host: e.target.value})}
      className="w-full px-3 py-2 border rounded-lg"
    />
  </div>
);

const TelegramConfig = ({ config, onChange }) => (
  <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
    <input
      type="text"
      placeholder="Bot Token (depuis @BotFather)"
      value={config.bot_token || ''}
      onChange={(e) => onChange({...config, bot_token: e.target.value})}
      className="w-full px-3 py-2 border rounded-lg"
    />
    <input
      type="text"
      placeholder="Chat ID"
      value={config.chat_id || ''}
      onChange={(e) => onChange({...config, chat_id: e.target.value})}
      className="w-full px-3 py-2 border rounded-lg"
    />
  </div>
);

const DiscordConfig = ({ config, onChange }) => (
  <div className="p-4 bg-gray-50 rounded-lg">
    <input
      type="text"
      placeholder="URL du Webhook Discord"
      value={config.webhook_url || ''}
      onChange={(e) => onChange({...config, webhook_url: e.target.value})}
      className="w-full px-3 py-2 border rounded-lg"
    />
  </div>
);

const WebhookConfig = ({ config, onChange }) => (
  <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
    <input
      type="text"
      placeholder="URL du Webhook"
      value={config.url || ''}
      onChange={(e) => onChange({...config, url: e.target.value})}
      className="w-full px-3 py-2 border rounded-lg"
    />
    <select
      value={config.method || 'POST'}
      onChange={(e) => onChange({...config, method: e.target.value})}
      className="w-full px-3 py-2 border rounded-lg"
    >
      <option value="POST">POST</option>
      <option value="PUT">PUT</option>
    </select>
  </div>
);

export default NotificationsConfig;
