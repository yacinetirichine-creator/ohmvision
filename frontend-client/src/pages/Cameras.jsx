/**
 * OhmVision - Cameras Page
 */

import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Camera,
  Plus,
  Search,
  Filter,
  Grid,
  List,
  Wifi,
  WifiOff,
  MoreVertical,
  Settings,
  Trash2,
  Eye,
  X
} from 'lucide-react';
import { useCamerasStore, useUIStore } from '../services/store';

// Add Camera Modal
const AddCameraModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    rtsp_url: '',
    ip_address: '',
    username: '',
    password: ''
  });
  
  if (!isOpen) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-dark-800 rounded-2xl p-6 w-full max-w-lg border border-dark-600"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Ajouter une caméra</h2>
          <button onClick={onClose} className="p-2 hover:bg-dark-700 rounded-lg">
            <X size={20} />
          </button>
        </div>
        
        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Nom de la caméra *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Ex: Entrée principale"
              className="w-full bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 focus:outline-none focus:border-primary"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Emplacement</label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="Ex: Bâtiment A, RDC"
              className="w-full bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 focus:outline-none focus:border-primary"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Adresse IP</label>
              <input
                type="text"
                value={formData.ip_address}
                onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                placeholder="192.168.1.100"
                className="w-full bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Port RTSP</label>
              <input
                type="text"
                value="554"
                disabled
                className="w-full bg-dark-900 border border-dark-600 rounded-xl px-4 py-3 text-gray-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">URL RTSP (optionnel)</label>
            <input
              type="text"
              value={formData.rtsp_url}
              onChange={(e) => setFormData({ ...formData, rtsp_url: e.target.value })}
              placeholder="rtsp://192.168.1.100:554/stream1"
              className="w-full bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 focus:outline-none focus:border-primary font-mono text-sm"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Utilisateur</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="admin"
                className="w-full bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Mot de passe</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="••••••••"
                className="w-full bg-dark-700 border border-dark-600 rounded-xl px-4 py-3 focus:outline-none focus:border-primary"
              />
            </div>
          </div>
          
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 border border-dark-600 rounded-xl hover:bg-dark-700 transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-3 bg-primary hover:bg-primary-dark text-white rounded-xl transition-colors"
            >
              Ajouter
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

// Camera Card
const CameraCard = ({ camera, viewMode }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  
  if (viewMode === 'list') {
    return (
      <motion.div
        layout
        className="bg-dark-800 rounded-xl p-4 border border-dark-600 flex items-center gap-4"
      >
        <div className={`w-3 h-3 rounded-full ${camera.is_online ? 'bg-success' : 'bg-danger'}`} />
        
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold truncate">{camera.name}</h3>
          <p className="text-sm text-gray-400 truncate">{camera.location || camera.ip_address}</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Link
            to={`/cameras/${camera.id}`}
            className="p-2 hover:bg-dark-700 rounded-lg"
          >
            <Eye size={18} />
          </Link>
          <Link
            to={`/cameras/${camera.id}?settings=true`}
            className="p-2 hover:bg-dark-700 rounded-lg"
          >
            <Settings size={18} />
          </Link>
        </div>
      </motion.div>
    );
  }
  
  return (
    <motion.div
      layout
      className="bg-dark-800 rounded-2xl overflow-hidden border border-dark-600 group"
    >
      <Link to={`/cameras/${camera.id}`}>
        <div className="relative aspect-video bg-dark-700">
          <div className="absolute inset-0 flex items-center justify-center">
            <Camera size={40} className="text-gray-600" />
          </div>
          
          <div className={`absolute top-3 left-3 flex items-center gap-2 px-2 py-1 rounded-full text-xs font-medium ${
            camera.is_online
              ? 'bg-success/20 text-success'
              : 'bg-danger/20 text-danger'
          }`}>
            {camera.is_online ? <Wifi size={12} /> : <WifiOff size={12} />}
            {camera.is_online ? 'En ligne' : 'Hors ligne'}
          </div>
          
          {camera.is_online && (
            <div className="absolute top-3 right-3 flex items-center gap-1 px-2 py-1 bg-danger rounded-full text-xs font-medium">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
              LIVE
            </div>
          )}
          
          <div className="absolute inset-0 bg-gradient-to-t from-dark-900/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </Link>
      
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold truncate">{camera.name}</h3>
            <p className="text-sm text-gray-400 truncate">
              {camera.location || camera.ip_address || 'Non configuré'}
            </p>
          </div>
          
          <div className="relative">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-2 hover:bg-dark-700 rounded-lg"
            >
              <MoreVertical size={18} />
            </button>
            
            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="absolute right-0 top-full mt-1 bg-dark-700 border border-dark-600 rounded-xl shadow-lg overflow-hidden z-10 w-40"
                >
                  <Link
                    to={`/cameras/${camera.id}`}
                    className="flex items-center gap-2 px-4 py-2 hover:bg-dark-600 transition-colors"
                  >
                    <Eye size={16} /> Voir
                  </Link>
                  <Link
                    to={`/cameras/${camera.id}?settings=true`}
                    className="flex items-center gap-2 px-4 py-2 hover:bg-dark-600 transition-colors"
                  >
                    <Settings size={16} /> Paramètres
                  </Link>
                  <button
                    className="flex items-center gap-2 px-4 py-2 hover:bg-danger/10 text-danger w-full transition-colors"
                  >
                    <Trash2 size={16} /> Supprimer
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
        
        {/* Detection badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          {camera.detection_config?.person_detection && (
            <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
              👤 Personnes
            </span>
          )}
          {camera.detection_config?.counting && (
            <span className="px-2 py-1 bg-purple/10 text-purple text-xs rounded-full">
              📊 Comptage
            </span>
          )}
          {camera.detection_config?.fall_detection && (
            <span className="px-2 py-1 bg-warning/10 text-warning text-xs rounded-full">
              ⬇️ Chute
            </span>
          )}
          {camera.detection_config?.ppe_detection && (
            <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">
              🦺 EPI
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Main Page
export default function Cameras() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { cameras, fetchCameras, isLoading } = useCamerasStore();
  
  const [viewMode, setViewMode] = useState('grid');
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all'); // all, online, offline
  const [showAddModal, setShowAddModal] = useState(searchParams.get('add') === 'true');
  
  useEffect(() => {
    fetchCameras();
  }, []);
  
  // Filter cameras
  const filteredCameras = cameras.filter((camera) => {
    const matchesSearch = camera.name.toLowerCase().includes(search.toLowerCase()) ||
                         camera.location?.toLowerCase().includes(search.toLowerCase());
    
    if (filter === 'online') return matchesSearch && camera.is_online;
    if (filter === 'offline') return matchesSearch && !camera.is_online;
    return matchesSearch;
  });
  
  const onlineCount = cameras.filter((c) => c.is_online).length;
  const offlineCount = cameras.filter((c) => !c.is_online).length;
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Caméras</h1>
          <p className="text-gray-400">
            {cameras.length} caméra{cameras.length > 1 ? 's' : ''} • 
            <span className="text-success"> {onlineCount} en ligne</span> • 
            <span className="text-danger"> {offlineCount} hors ligne</span>
          </p>
        </div>
        
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-xl transition-colors"
        >
          <Plus size={20} />
          <span>Ajouter</span>
        </button>
      </div>
      
      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher une caméra..."
            className="w-full bg-dark-800 border border-dark-600 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:border-primary"
          />
        </div>
        
        {/* Filter buttons */}
        <div className="flex items-center gap-2">
          <div className="flex bg-dark-800 border border-dark-600 rounded-xl p-1">
            {[
              { value: 'all', label: 'Toutes' },
              { value: 'online', label: 'En ligne' },
              { value: 'offline', label: 'Hors ligne' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => setFilter(option.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === option.value
                    ? 'bg-primary text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
          
          {/* View mode toggle */}
          <div className="flex bg-dark-800 border border-dark-600 rounded-xl p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'grid' ? 'bg-primary text-white' : 'text-gray-400'
              }`}
            >
              <Grid size={20} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'list' ? 'bg-primary text-white' : 'text-gray-400'
              }`}
            >
              <List size={20} />
            </button>
          </div>
        </div>
      </div>
      
      {/* Camera Grid/List */}
      {filteredCameras.length === 0 ? (
        <div className="bg-dark-800 rounded-2xl p-12 text-center border border-dark-600">
          <Camera size={64} className="mx-auto text-gray-600 mb-4" />
          <h3 className="text-xl font-semibold mb-2">
            {search || filter !== 'all' ? 'Aucun résultat' : 'Aucune caméra'}
          </h3>
          <p className="text-gray-400 mb-6">
            {search || filter !== 'all'
              ? 'Essayez de modifier vos filtres'
              : 'Ajoutez votre première caméra pour commencer'}
          </p>
          {!search && filter === 'all' && (
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center gap-2 bg-primary hover:bg-primary-dark text-white px-6 py-3 rounded-xl transition-colors"
            >
              <Plus size={20} />
              Ajouter une caméra
            </button>
          )}
        </div>
      ) : (
        <motion.div
          layout
          className={viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
            : 'space-y-3'
          }
        >
          <AnimatePresence>
            {filteredCameras.map((camera) => (
              <CameraCard key={camera.id} camera={camera} viewMode={viewMode} />
            ))}
          </AnimatePresence>
        </motion.div>
      )}
      
      {/* Add Camera Modal */}
      <AnimatePresence>
        <AddCameraModal
          isOpen={showAddModal}
          onClose={() => {
            setShowAddModal(false);
            setSearchParams({});
          }}
        />
      </AnimatePresence>
    </div>
  );
}
