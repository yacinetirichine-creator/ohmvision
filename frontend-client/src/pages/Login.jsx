/**
 * OhmVision - Login Page
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../services/store';

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(email, password);
    if (result.success) {
      navigate('/dashboard');
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-dark-800 rounded-2xl p-8 border border-dark-600 shadow-xl"
    >
      <h2 className="text-2xl font-bold mb-2">{t('auth.login.title')}</h2>
      <p className="text-gray-400 mb-6">
        {t('auth.login.subtitle')}
      </p>
      
      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-danger/10 border border-danger/30 text-danger rounded-xl p-4 mb-6"
        >
          {error}
        </motion.div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email */}
        <div>
          <label className="block text-sm font-medium mb-2">{t('auth.fields.email')}</label>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('auth.placeholders.email')}
              required
              className="w-full bg-dark-700 border border-dark-600 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:border-primary transition-colors"
            />
          </div>
        </div>
        
        {/* Password */}
        <div>
          <label className="block text-sm font-medium mb-2">{t('auth.fields.password')}</label>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t('auth.placeholders.password')}
              required
              className="w-full bg-dark-700 border border-dark-600 rounded-xl pl-12 pr-12 py-3 focus:outline-none focus:border-primary transition-colors"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
        </div>
        
        {/* Remember & Forgot */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" className="w-4 h-4 rounded bg-dark-700 border-dark-600" />
            <span className="text-sm text-gray-400">{t('auth.login.rememberMe')}</span>
          </label>
          <a href="#" className="text-sm text-primary hover:underline">
            {t('auth.login.forgotPassword')}
          </a>
        </div>
        
        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-primary hover:bg-primary-dark text-white font-semibold py-3 rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              {t('auth.login.loading')}
            </>
          ) : (
            t('auth.login.submit')
          )}
        </button>
      </form>
      
      {/* Demo credentials */}
      <div className="mt-6 p-4 bg-dark-700/50 rounded-xl">
        <p className="text-sm text-gray-400 mb-2">{t('auth.login.demoAccount')}</p>
        <p className="text-sm font-mono">demo@ohmvision.fr / demo123</p>
      </div>
    </motion.div>
  );
}
