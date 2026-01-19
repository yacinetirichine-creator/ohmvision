/**
 * OhmVision - AI Assistant Page
 * Interface de chat avec l'Agent IA
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot, Send, Sparkles, AlertCircle, CheckCircle, Lightbulb,
  RefreshCw, Zap, Camera, Settings, ChevronRight, MessageSquare
} from 'lucide-react';
import { useAIStore, useCamerasStore } from '../services/store';

const AIAssistant = () => {
  const { messages, suggestions, isTyping, sendMessage, runDiagnostic, getSuggestions, clearMessages } = useAIStore();
  const { cameras, fetchCameras } = useCamerasStore();
  
  const [input, setInput] = useState('');
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [diagnosticResult, setDiagnosticResult] = useState(null);
  const messagesEndRef = useRef(null);
  
  useEffect(() => {
    fetchCameras();
    getSuggestions();
  }, []);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSend = async () => {
    if (!input.trim()) return;
    
    const message = input;
    setInput('');
    setShowQuickActions(false);
    
    await sendMessage(message);
  };
  
  const handleQuickAction = async (action) => {
    setShowQuickActions(false);
    
    switch (action) {
      case 'diagnostic':
        const result = await runDiagnostic();
        setDiagnosticResult(result);
        break;
      case 'optimize':
        await sendMessage("Optimise mes caméras pour réduire les faux positifs");
        break;
      case 'report':
        await sendMessage("Génère un rapport de la semaine dernière");
        break;
      case 'help':
        await sendMessage("Quelles sont les fonctionnalités disponibles ?");
        break;
      default:
        await sendMessage(action);
    }
  };
  
  const quickActions = [
    {
      id: 'diagnostic',
      icon: Zap,
      title: 'Diagnostic système',
      description: 'Analyse complète de toutes les caméras',
      color: 'primary'
    },
    {
      id: 'optimize',
      icon: Settings,
      title: 'Optimiser les détections',
      description: 'Réduire les faux positifs automatiquement',
      color: 'purple'
    },
    {
      id: 'report',
      icon: MessageSquare,
      title: 'Générer un rapport',
      description: 'Rapport de la semaine dernière',
      color: 'success'
    },
    {
      id: 'help',
      icon: Lightbulb,
      title: 'Aide & Conseils',
      description: 'Découvrir les fonctionnalités',
      color: 'warning'
    }
  ];
  
  const suggestionMessages = [
    "Pourquoi ma caméra Entrée est hors ligne ?",
    "Comment configurer la détection de chute ?",
    "Montre-moi les alertes critiques d'aujourd'hui",
    "Quels sont les pics de fréquentation ?",
  ];
  
  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] lg:h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-purple to-primary rounded-2xl flex items-center justify-center">
            <Bot size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold">Assistant IA</h1>
            <p className="text-sm text-gray-500">Posez vos questions, je suis là pour vous aider</p>
          </div>
        </div>
        
        {messages.length > 0 && (
          <button
            onClick={clearMessages}
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg"
          >
            Nouvelle conversation
          </button>
        )}
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto bg-dark-800 rounded-2xl p-4 space-y-4">
        {/* Quick Actions (when no messages) */}
        {messages.length === 0 && showQuickActions && (
          <div className="space-y-6">
            {/* Welcome */}
            <div className="text-center py-8">
              <div className="w-20 h-20 bg-gradient-to-br from-purple/20 to-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles size={36} className="text-primary" />
              </div>
              <h2 className="text-xl font-bold mb-2">Comment puis-je vous aider ?</h2>
              <p className="text-gray-500 max-w-md mx-auto">
                Je peux diagnostiquer vos caméras, optimiser les détections, générer des rapports et répondre à toutes vos questions.
              </p>
            </div>
            
            {/* Quick Action Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {quickActions.map((action) => (
                <motion.button
                  key={action.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleQuickAction(action.id)}
                  className={`p-4 bg-dark-700 hover:bg-dark-600 rounded-xl text-left flex items-start gap-3`}
                >
                  <div className={`w-10 h-10 rounded-lg bg-${action.color}/20 flex items-center justify-center flex-shrink-0`}>
                    <action.icon size={20} className={`text-${action.color}`} />
                  </div>
                  <div>
                    <p className="font-medium">{action.title}</p>
                    <p className="text-sm text-gray-500">{action.description}</p>
                  </div>
                  <ChevronRight size={18} className="text-gray-600 ml-auto self-center" />
                </motion.button>
              ))}
            </div>
            
            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div>
                <p className="text-sm text-gray-500 mb-3">💡 Suggestions pour vous</p>
                <div className="space-y-2">
                  {suggestions.slice(0, 3).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleQuickAction(suggestion.message)}
                      className="w-full p-3 bg-dark-700/50 hover:bg-dark-600 rounded-lg text-left text-sm"
                    >
                      {suggestion.message}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Sample Questions */}
            <div>
              <p className="text-sm text-gray-500 mb-3">Essayez de demander :</p>
              <div className="flex flex-wrap gap-2">
                {suggestionMessages.map((msg, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(msg)}
                    className="px-3 py-1.5 bg-dark-700 hover:bg-dark-600 rounded-full text-sm"
                  >
                    {msg}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Diagnostic Result */}
        {diagnosticResult && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-dark-700 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <Zap size={18} className="text-primary" />
              <span className="font-medium">Résultat du diagnostic</span>
            </div>
            
            {diagnosticResult.issues_found?.length > 0 ? (
              <div className="space-y-2 mb-4">
                {diagnosticResult.issues_found.map((issue, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg ${
                      issue.severity === 'high' ? 'bg-danger/10 border border-danger/30' :
                      issue.severity === 'medium' ? 'bg-warning/10 border border-warning/30' :
                      'bg-dark-600'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <AlertCircle size={16} className={
                        issue.severity === 'high' ? 'text-danger' :
                        issue.severity === 'medium' ? 'text-warning' : 'text-gray-400'
                      } />
                      <span className="font-medium">{issue.message}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-3 bg-success/10 border border-success/30 rounded-lg mb-4">
                <div className="flex items-center gap-2 text-success">
                  <CheckCircle size={16} />
                  <span>Aucun problème détecté !</span>
                </div>
              </div>
            )}
            
            {diagnosticResult.recommendations?.length > 0 && (
              <div>
                <p className="text-sm text-gray-500 mb-2">Recommandations :</p>
                <ul className="space-y-1">
                  {diagnosticResult.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <span className="text-primary">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {diagnosticResult.auto_fixes_applied?.length > 0 && (
              <div className="mt-3 pt-3 border-t border-dark-600">
                <p className="text-sm text-success flex items-center gap-2">
                  <CheckCircle size={14} />
                  {diagnosticResult.auto_fixes_applied.length} correction(s) automatique(s) appliquée(s)
                </p>
              </div>
            )}
            
            <button
              onClick={() => setDiagnosticResult(null)}
              className="mt-4 text-sm text-gray-400 hover:text-white"
            >
              Fermer
            </button>
          </motion.div>
        )}
        
        {/* Chat Messages */}
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : ''}`}>
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 bg-gradient-to-br from-purple to-primary rounded-full flex items-center justify-center">
                    <Bot size={14} />
                  </div>
                  <span className="text-sm text-gray-500">Assistant IA</span>
                </div>
              )}
              
              <div className={`p-4 rounded-2xl ${
                message.role === 'user'
                  ? 'bg-primary text-white rounded-br-md'
                  : 'bg-dark-700 rounded-bl-md'
              }`}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Actions taken */}
                {message.actions?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/20 space-y-1">
                    {message.actions.map((action, index) => (
                      <p key={index} className="text-sm opacity-80">{action}</p>
                    ))}
                  </div>
                )}
                
                {/* Suggestions */}
                {message.suggestions?.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleQuickAction(suggestion)}
                        className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-full text-sm"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              <p className="text-xs text-gray-600 mt-1 px-2">
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </motion.div>
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2"
          >
            <div className="w-6 h-6 bg-gradient-to-br from-purple to-primary rounded-full flex items-center justify-center">
              <Bot size={14} />
            </div>
            <div className="bg-dark-700 rounded-2xl px-4 py-3 rounded-bl-md">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="mt-4">
        <div className="flex items-center gap-3 bg-dark-800 rounded-2xl p-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Posez votre question..."
            className="flex-1 bg-transparent px-4 py-3 focus:outline-none"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className={`p-3 rounded-xl ${
              input.trim() && !isTyping
                ? 'bg-primary hover:bg-primary-dark text-white'
                : 'bg-dark-700 text-gray-500'
            }`}
          >
            <Send size={20} />
          </button>
        </div>
        
        <p className="text-xs text-gray-600 text-center mt-2">
          L'IA peut faire des erreurs. Vérifiez les informations importantes.
        </p>
      </div>
    </div>
  );
};

export default AIAssistant;
