/**
 * OhmVision - AI Assistant Page
 * Interface de chat avec l'Agent IA
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot, Send, Sparkles, AlertCircle, CheckCircle, Lightbulb,
  RefreshCw, Zap, Camera, Settings, ChevronRight, MessageSquare, Activity
} from 'lucide-react';
import { useAIStore, useCamerasStore } from '../services/store';

const AIAssistant = () => {
  const { messages, suggestions, isTyping, sendMessage, runDiagnostic, getSuggestions, clearMessages } = useAIStore();
  const { cameras, fetchCameras } = useCamerasStore();
  
  const [input, setInput] = useState('');
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [diagnosticResult, setDiagnosticResult] = useState(null);
  const messagesEndRef = useRef(null);
  
  // New States for Visual Effects
  const [audioInputLevel, setAudioInputLevel] = useState(0);

  useEffect(() => {
    fetchCameras();
    getSuggestions();
    
    // Simulate AI "Thinking" pulse
    const interval = setInterval(() => {
        setAudioInputLevel(Math.random() * 100);
    }, 100);
    return () => clearInterval(interval);
  }, []);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSend = async (text = null) => {
    const messageToSend = text || input;
    if (!messageToSend.trim()) return;
    
    setInput('');
    setShowQuickActions(false);
    
    await sendMessage(messageToSend);
  };
  
  const handleQuickAction = async (action) => {
    setShowQuickActions(false);
    
    switch (action) {
      case 'diagnostic':
        const result = await runDiagnostic();
        setDiagnosticResult(result);
        break;
      case 'optimize':
        await handleSend("Optimise mes caméras pour réduire les faux positifs");
        break;
      case 'report':
        await handleSend("Génère un rapport de la semaine dernière");
        break;
      case 'help':
        await handleSend("Quelles sont les fonctionnalités disponibles ?");
        break;
      default:
        await handleSend(action);
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
    <div className="flex h-[calc(100vh-100px)] gap-6">
      <div className="flex-1 flex flex-col bg-dark-800/50 backdrop-blur-sm rounded-2xl border border-white/5 overflow-hidden shadow-2xl relative">
        {/* Header */}
        <div className="p-4 border-b border-white/5 bg-dark-900/50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br from-ohm-cyan to-ohm-blue flex items-center justify-center shadow-[0_0_15px_rgba(0,240,255,0.3)] transition-all duration-300 ${isTyping ? 'animate-pulse' : ''}`}>
              <Bot size={24} className="text-dark-950" />
            </div>
            <div>
              <h2 className="font-bold flex items-center gap-2">
                OhmVision AI
                <span className="text-[10px] bg-ohm-cyan/10 text-ohm-cyan border border-ohm-cyan/20 px-1.5 py-0.5 rounded uppercase tracking-wider">Beta</span>
              </h2>
              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                <span className={`w-1.5 h-1.5 rounded-full ${isTyping ? 'bg-ohm-cyan animate-ping' : 'bg-green-500'}`} />
                {isTyping ? 'Analyse en cours...' : 'Prêt à aider'}
              </div>
            </div>
          </div>
          
          <button 
            onClick={clearMessages}
            className="p-2 hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors"
            title="Effacer la conversation"
          >
            <RefreshCw size={18} />
          </button>
        </div>
        
        {/* Messages with futuristic background */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 relative">
          <div className="absolute inset-0 pointer-events-none opacity-5 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-ohm-cyan via-transparent to-transparent"></div>
          
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center h-full text-center p-8 text-gray-400"
              >
                <div className="w-24 h-24 bg-dark-800 rounded-full flex items-center justify-center mb-6 border border-white/5 relative group">
                    <div className="absolute inset-0 bg-ohm-cyan/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <Bot size={48} className="text-ohm-cyan/50" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Comment puis-je vous aider ?</h3>
                <p className="max-w-md mx-auto mb-8">
                  Je peux analyser vos flux vidéo, optimiser les réglages de détection ou générer des rapports de sécurité.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                  {suggestionMessages.map((msg, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(msg)}
                      className="text-left p-4 rounded-xl bg-dark-900/50 border border-white/5 hover:border-ohm-cyan/50 hover:bg-dark-800 transition-all text-sm group"
                    >
                      <span className="text-gray-300 group-hover:text-white transition-colors">{msg}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                layout
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`
                  max-w-[80%] rounded-2xl p-4 shadow-lg backdrop-blur-sm border
                  ${msg.role === 'user'
                    ? 'bg-gradient-to-r from-ohm-blue to-ohm-cyan text-white rounded-br-none border-transparent' 
                    : 'bg-dark-900/80 border-white/10 rounded-bl-none text-gray-100'}
                `}>
                  <p className="whitespace-pre-wrap">{msg.content || msg.text}</p>
                </div>
              </motion.div>
            ))}
            
            {/* Visualisation de la "pensée" de l'IA */}
            {isTyping && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                 <div className="bg-dark-900/80 border border-white/10 rounded-2xl rounded-bl-none p-4 flex items-center gap-2">
                    <span className="w-2 h-2 bg-ohm-cyan rounded-full animate-bounce delay-75"></span>
                    <span className="w-2 h-2 bg-ohm-cyan rounded-full animate-bounce delay-150"></span>
                    <span className="w-2 h-2 bg-ohm-cyan rounded-full animate-bounce delay-300"></span>
                 </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </AnimatePresence>
        </div>

        {/* Input Area */}
        <div className="p-4 bg-dark-900/80 border-t border-white/5">
           {/* Quick Actions Scroll */}
           <AnimatePresence>
             {messages.length > 0 && (
               <motion.div 
                 initial={{ opacity: 0, height: 0 }}
                 animate={{ opacity: 1, height: 'auto' }}
                 className="flex gap-2 mb-4 overflow-x-auto pb-2 no-scrollbar"
               >
                  {quickActions.map(action => (
                     <button 
                       key={action.id}
                       onClick={() => handleQuickAction(action.id)}
                       className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:border-ohm-cyan/50 hover:bg-white/10 transition-all text-xs font-medium whitespace-nowrap"
                     >
                        <action.icon size={12} className={`text-${action.color === 'primary' ? 'ohm-cyan' : action.color}`} />
                        {action.title}
                     </button>
                  ))}
               </motion.div>
             )}
           </AnimatePresence>

           <div className="relative">
             <input
               type="text"
               value={input}
               onChange={(e) => setInput(e.target.value)}
               onKeyDown={(e) => e.key === 'Enter' && handleSend()}
               placeholder="Posez une question sur votre système de sécurité..."
               className="w-full bg-dark-950 border border-dark-700 rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:border-ohm-cyan/50 focus:ring-1 focus:ring-ohm-cyan/50 transition-all placeholder-gray-600 text-white"
             />
             <button
               onClick={() => handleSend()}
               disabled={!input.trim() || isTyping}
               className="absolute right-2 top-2 p-1.5 bg-ohm-cyan text-dark-950 rounded-lg hover:bg-white hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 transition-all shadow-neon"
             >
               <Send size={18} />
             </button>
           </div>
        </div>
      </div>
      
      {/* Right Sidebar - Context & Status */}
      <div className="w-80 hidden lg:flex flex-col gap-4">
         <div className="glass-card p-4">
            <h3 className="font-bold mb-4 flex items-center gap-2 text-sm text-gray-300">
               <Activity size={16} className="text-ohm-cyan" />
               ÉTAT DU SYSTÈME
            </h3>
            <div className="space-y-4">
               <div>
                  <div className="flex justify-between text-xs mb-1">
                     <span className="text-gray-500">Charge CPU IA</span>
                     <span className="text-ohm-cyan font-mono">42%</span>
                  </div>
                  <div className="h-1.5 bg-dark-700 rounded-full overflow-hidden">
                     <div className="h-full bg-ohm-cyan w-[42%] shadow-[0_0_10px_#00f0ff]"></div>
                  </div>
               </div>
               <div>
                  <div className="flex justify-between text-xs mb-1">
                     <span className="text-gray-500">Bande Passante</span>
                     <span className="text-ohm-blue font-mono">24 MB/s</span>
                  </div>
                  <div className="h-1.5 bg-dark-700 rounded-full overflow-hidden">
                     <div className="h-full bg-ohm-blue w-[65%]"></div>
                  </div>
               </div>
            </div>
         </div>
         
         <div className="glass-card p-4 flex-1">
            <h3 className="font-bold mb-4 flex items-center gap-2 text-sm text-gray-300">
               <Sparkles size={16} className="text-ohm-purple" />
               SUGGESTIONS
            </h3>
            <div className="space-y-3">
               {["Optimiser caméra #04", "Vérifier logs d'hier soir", "Exporter incident 22h30"].map((item, i) => (
                  <div key={i} className="p-3 bg-white/5 rounded-lg text-xs hover:bg-white/10 cursor-pointer border border-transparent hover:border-white/10 transition-colors">
                     {item}
                  </div>
               ))}
            </div>
         </div>
      </div>
    </div>
  );
};

export default AIAssistant;
