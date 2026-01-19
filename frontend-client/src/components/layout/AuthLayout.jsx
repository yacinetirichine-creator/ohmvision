/**
 * OhmVision - Auth Layout
 */

import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuthStore } from '../../services/store';

export default function AuthLayout() {
  const { isAuthenticated } = useAuthStore();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return (
    <div className="min-h-screen bg-dark-900 flex flex-col items-center justify-center p-4">
      {/* Background pattern */}
      <div className="fixed inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />
      </div>
      
      {/* Logo */}
      <div className="mb-8 text-center relative z-10">
        <div className="w-20 h-20 bg-gradient-to-br from-primary to-purple rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/20">
          <span className="text-4xl">👁️</span>
        </div>
        <h1 className="text-3xl font-bold">OhmVision</h1>
        <p className="text-gray-400 mt-2">Analyse vidéo intelligente</p>
      </div>
      
      {/* Content */}
      <div className="w-full max-w-md relative z-10">
        <Outlet />
      </div>
      
      {/* Footer */}
      <p className="mt-8 text-sm text-gray-500 relative z-10">
        © 2025 Ohmtronic. Tous droits réservés.
      </p>
    </div>
  );
}
