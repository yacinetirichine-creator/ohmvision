/**
 * OhmVision - Theme System
 * Système de thèmes avec mode sombre/clair et personnalisation
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { Sun, Moon, Palette, Check } from 'lucide-react';

// Available themes
export const THEMES = {
  dark: {
    id: 'dark',
    name: 'Sombre',
    icon: Moon,
    colors: {
      // Backgrounds
      'bg-primary': '#0f0f1a',
      'bg-secondary': '#1a1a2e',
      'bg-tertiary': '#252542',
      'bg-card': '#1e1e35',
      
      // Text
      'text-primary': '#ffffff',
      'text-secondary': '#a0aec0',
      'text-muted': '#718096',
      
      // Borders
      'border-primary': '#2d2d4a',
      'border-secondary': '#3d3d5c',
      
      // Accents
      'accent-primary': '#6366f1',
      'accent-secondary': '#8b5cf6',
      'accent-success': '#22c55e',
      'accent-warning': '#f59e0b',
      'accent-danger': '#ef4444',
      'accent-info': '#3b82f6',
    }
  },
  light: {
    id: 'light',
    name: 'Clair',
    icon: Sun,
    colors: {
      // Backgrounds
      'bg-primary': '#f8fafc',
      'bg-secondary': '#ffffff',
      'bg-tertiary': '#f1f5f9',
      'bg-card': '#ffffff',
      
      // Text
      'text-primary': '#1e293b',
      'text-secondary': '#475569',
      'text-muted': '#94a3b8',
      
      // Borders
      'border-primary': '#e2e8f0',
      'border-secondary': '#cbd5e1',
      
      // Accents (same as dark)
      'accent-primary': '#6366f1',
      'accent-secondary': '#8b5cf6',
      'accent-success': '#22c55e',
      'accent-warning': '#f59e0b',
      'accent-danger': '#ef4444',
      'accent-info': '#3b82f6',
    }
  },
  midnight: {
    id: 'midnight',
    name: 'Minuit',
    icon: Moon,
    colors: {
      'bg-primary': '#0a0a0f',
      'bg-secondary': '#12121a',
      'bg-tertiary': '#1a1a24',
      'bg-card': '#15151f',
      'text-primary': '#e2e8f0',
      'text-secondary': '#94a3b8',
      'text-muted': '#64748b',
      'border-primary': '#1e1e2d',
      'border-secondary': '#2a2a3d',
      'accent-primary': '#818cf8',
      'accent-secondary': '#a78bfa',
      'accent-success': '#34d399',
      'accent-warning': '#fbbf24',
      'accent-danger': '#f87171',
      'accent-info': '#60a5fa',
    }
  },
  ocean: {
    id: 'ocean',
    name: 'Océan',
    icon: Palette,
    colors: {
      'bg-primary': '#0c1929',
      'bg-secondary': '#132337',
      'bg-tertiary': '#1a2e45',
      'bg-card': '#152a40',
      'text-primary': '#e2e8f0',
      'text-secondary': '#94a3b8',
      'text-muted': '#64748b',
      'border-primary': '#1e3a5f',
      'border-secondary': '#2a4a6f',
      'accent-primary': '#0ea5e9',
      'accent-secondary': '#06b6d4',
      'accent-success': '#22c55e',
      'accent-warning': '#f59e0b',
      'accent-danger': '#ef4444',
      'accent-info': '#38bdf8',
    }
  },
  forest: {
    id: 'forest',
    name: 'Forêt',
    icon: Palette,
    colors: {
      'bg-primary': '#0f1a14',
      'bg-secondary': '#152920',
      'bg-tertiary': '#1c352a',
      'bg-card': '#182e24',
      'text-primary': '#e2e8f0',
      'text-secondary': '#94a3b8',
      'text-muted': '#64748b',
      'border-primary': '#1e4033',
      'border-secondary': '#2a5043',
      'accent-primary': '#22c55e',
      'accent-secondary': '#10b981',
      'accent-success': '#34d399',
      'accent-warning': '#fbbf24',
      'accent-danger': '#f87171',
      'accent-info': '#60a5fa',
    }
  },
  sunset: {
    id: 'sunset',
    name: 'Coucher de soleil',
    icon: Palette,
    colors: {
      'bg-primary': '#1a0f14',
      'bg-secondary': '#2a1520',
      'bg-tertiary': '#3a1c2a',
      'bg-card': '#2e1824',
      'text-primary': '#fce7f3',
      'text-secondary': '#f9a8d4',
      'text-muted': '#f472b6',
      'border-primary': '#4a1e30',
      'border-secondary': '#5a2840',
      'accent-primary': '#f43f5e',
      'accent-secondary': '#ec4899',
      'accent-success': '#22c55e',
      'accent-warning': '#fbbf24',
      'accent-danger': '#ef4444',
      'accent-info': '#60a5fa',
    }
  },
};

// Accent color presets
export const ACCENT_COLORS = [
  { id: 'indigo', name: 'Indigo', color: '#6366f1' },
  { id: 'purple', name: 'Violet', color: '#8b5cf6' },
  { id: 'blue', name: 'Bleu', color: '#3b82f6' },
  { id: 'cyan', name: 'Cyan', color: '#06b6d4' },
  { id: 'teal', name: 'Teal', color: '#14b8a6' },
  { id: 'green', name: 'Vert', color: '#22c55e' },
  { id: 'orange', name: 'Orange', color: '#f97316' },
  { id: 'red', name: 'Rouge', color: '#ef4444' },
  { id: 'pink', name: 'Rose', color: '#ec4899' },
];

// Theme context
const ThemeContext = createContext(null);

// Theme provider component
export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('ohmvision-theme');
    return saved || 'dark';
  });
  
  const [accentColor, setAccentColor] = useState(() => {
    const saved = localStorage.getItem('ohmvision-accent');
    return saved || 'indigo';
  });
  
  const [customColors, setCustomColors] = useState({});

  // Apply theme to document
  useEffect(() => {
    const themeData = THEMES[theme];
    const accent = ACCENT_COLORS.find(a => a.id === accentColor);
    
    if (themeData) {
      const root = document.documentElement;
      
      // Apply theme colors as CSS variables
      Object.entries(themeData.colors).forEach(([key, value]) => {
        root.style.setProperty(`--${key}`, value);
      });
      
      // Apply accent color
      if (accent) {
        root.style.setProperty('--accent-primary', accent.color);
      }
      
      // Apply custom colors
      Object.entries(customColors).forEach(([key, value]) => {
        root.style.setProperty(`--${key}`, value);
      });
      
      // Set body class for theme
      document.body.className = `theme-${theme}`;
      
      // Save to localStorage
      localStorage.setItem('ohmvision-theme', theme);
      localStorage.setItem('ohmvision-accent', accentColor);
    }
  }, [theme, accentColor, customColors]);

  const value = {
    theme,
    setTheme,
    accentColor,
    setAccentColor,
    customColors,
    setCustomColors,
    themes: THEMES,
    accents: ACCENT_COLORS,
    isDark: theme !== 'light',
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook to use theme
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme toggle button component
export const ThemeToggle = ({ className = '' }) => {
  const { setTheme, isDark } = useTheme();
  
  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark');
  };

  return (
    <button
      onClick={toggleTheme}
      className={`
        p-2 rounded-xl transition-all duration-300
        bg-dark-700 hover:bg-dark-600
        ${className}
      `}
      title={isDark ? 'Mode clair' : 'Mode sombre'}
    >
      {isDark ? (
        <Sun size={18} className="text-yellow-400" />
      ) : (
        <Moon size={18} className="text-indigo-400" />
      )}
    </button>
  );
};

// Theme selector panel component
export const ThemeSelector = ({ onClose: _onClose }) => {
  const { theme, setTheme, accentColor, setAccentColor, themes, accents } = useTheme();

  return (
    <div className="p-4 space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Palette size={16} className="text-primary" />
          Thème
        </h3>
        
        <div className="grid grid-cols-2 gap-2">
          {Object.values(themes).map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.id}
                onClick={() => setTheme(t.id)}
                className={`
                  flex items-center gap-2 p-3 rounded-xl border transition-all
                  ${theme === t.id 
                    ? 'border-primary bg-primary/10' 
                    : 'border-dark-600 hover:border-dark-500 bg-dark-700/50'}
                `}
              >
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: t.colors['bg-secondary'] }}
                >
                  <Icon size={14} style={{ color: t.colors['accent-primary'] }} />
                </div>
                <span className="text-sm text-white">{t.name}</span>
                {theme === t.id && (
                  <Check size={14} className="text-primary ml-auto" />
                )}
              </button>
            );
          })}
        </div>
      </div>
      
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">
          Couleur d'accent
        </h3>
        
        <div className="flex flex-wrap gap-2">
          {accents.map((accent) => (
            <button
              key={accent.id}
              onClick={() => setAccentColor(accent.id)}
              className={`
                w-8 h-8 rounded-full transition-all
                ${accentColor === accent.id 
                  ? 'ring-2 ring-white ring-offset-2 ring-offset-dark-800 scale-110' 
                  : 'hover:scale-110'}
              `}
              style={{ backgroundColor: accent.color }}
              title={accent.name}
            />
          ))}
        </div>
      </div>
      
      <div className="pt-4 border-t border-dark-600">
        <h3 className="text-sm font-semibold text-white mb-3">
          Prévisualisation
        </h3>
        
        <div className="p-4 rounded-xl bg-dark-700/50 border border-dark-600">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <span className="text-white text-lg">👁️</span>
            </div>
            <div>
              <p className="font-semibold text-white">OhmVision</p>
              <p className="text-xs text-gray-400">Surveillance IA</p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <div className="flex-1 h-2 rounded-full bg-success" />
            <div className="flex-1 h-2 rounded-full bg-warning" />
            <div className="flex-1 h-2 rounded-full bg-danger" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThemeProvider;
