/**
 * OhmVision - MultiCameraView
 * Vue multi-caméras moderne avec overlay des détections en temps réel
 */

import React, { useState, useEffect } from 'react';
import { 
  Maximize2, Minimize2, Camera, AlertTriangle,
  Users, Car, TrendingUp,
  ChevronLeft, ChevronRight, Download,
  Fullscreen, PictureInPicture, RefreshCw, Eye, EyeOff
} from 'lucide-react';

// Layouts disponibles
const LAYOUTS = {
  '1x1': { cols: 1, rows: 1, total: 1 },
  '2x2': { cols: 2, rows: 2, total: 4 },
  '3x3': { cols: 3, rows: 3, total: 9 },
  '4x4': { cols: 4, rows: 4, total: 16 },
  '1+5': { cols: 3, rows: 2, total: 6, special: 'featured' },
  '2+8': { cols: 4, rows: 3, total: 10, special: 'dual-featured' },
};

// Composant pour une seule caméra avec overlay
const CameraFeed = ({ 
  camera, 
  isSelected, 
  onSelect, 
  onDoubleClick,
  showOverlay = true,
  showStats = true,
  size = 'normal' 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [detections, setDetections] = useState({
    persons: 0,
    vehicles: 0,
    alerts: []
  });
  
  // Simulation de détections en temps réel
  useEffect(() => {
    const interval = setInterval(() => {
      setDetections({
        persons: Math.floor(Math.random() * 15),
        vehicles: Math.floor(Math.random() * 5),
        alerts: Math.random() > 0.9 ? [{ type: 'motion', time: new Date() }] : []
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const sizeClasses = {
    small: 'text-xs',
    normal: 'text-sm',
    large: 'text-base'
  };

  return (
    <div 
      className={`
        relative rounded-xl overflow-hidden cursor-pointer
        transition-all duration-300 ease-out
        ${isSelected ? 'ring-2 ring-primary ring-offset-2 ring-offset-dark-900' : ''}
        ${isHovered ? 'scale-[1.02] z-10' : ''}
        bg-dark-800 group
      `}
      onClick={() => onSelect(camera.id)}
      onDoubleClick={() => onDoubleClick(camera.id)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Video Feed */}
      <div className="aspect-video bg-dark-900 relative">
        <img 
          src={`/api/streaming/mjpeg/${camera.id}`}
          alt={camera.name}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.target.src = '/placeholder-camera.jpg';
          }}
        />
        
        {/* Gradient overlay for better text readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40" />
        
        {/* Detection Overlays - Bounding Boxes */}
        {showOverlay && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {/* Simulated bounding boxes */}
            {detections.persons > 0 && (
              <>
                <rect 
                  x="20%" y="30%" width="15%" height="40%" 
                  fill="none" stroke="#22c55e" strokeWidth="2"
                  className="animate-pulse"
                />
                <text x="20%" y="28%" fill="#22c55e" fontSize="12">Person 87%</text>
              </>
            )}
            {detections.vehicles > 0 && (
              <>
                <rect 
                  x="60%" y="50%" width="25%" height="30%" 
                  fill="none" stroke="#3b82f6" strokeWidth="2"
                />
                <text x="60%" y="48%" fill="#3b82f6" fontSize="12">Vehicle 92%</text>
              </>
            )}
            
            {/* Zone de détection */}
            <polygon 
              points="10%,80% 30%,60% 70%,60% 90%,80%" 
              fill="rgba(99, 102, 241, 0.1)" 
              stroke="#6366f1" 
              strokeWidth="1"
              strokeDasharray="5,5"
            />
          </svg>
        )}
        
        {/* Live indicator */}
        <div className="absolute top-3 left-3 flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-500/90 backdrop-blur-sm">
            <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
            <span className="text-xs font-medium text-white">LIVE</span>
          </div>
          {camera.recording && (
            <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-orange-500/90 backdrop-blur-sm">
              <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
              <span className="text-xs font-medium text-white">REC</span>
            </div>
          )}
        </div>
        
        {/* Alert badge */}
        {detections.alerts.length > 0 && (
          <div className="absolute top-3 right-3 flex items-center gap-1 px-2 py-1 rounded-full bg-red-600/90 backdrop-blur-sm animate-pulse">
            <AlertTriangle size={14} className="text-white" />
            <span className="text-xs font-medium text-white">ALERT</span>
          </div>
        )}
        
        {/* Real-time stats overlay */}
        {showStats && (
          <div className="absolute top-3 right-3 flex flex-col gap-1">
            <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-black/60 backdrop-blur-sm">
              <Users size={14} className="text-green-400" />
              <span className={`font-mono text-green-400 ${sizeClasses[size]}`}>
                {detections.persons}
              </span>
            </div>
            <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-black/60 backdrop-blur-sm">
              <Car size={14} className="text-blue-400" />
              <span className={`font-mono text-blue-400 ${sizeClasses[size]}`}>
                {detections.vehicles}
              </span>
            </div>
          </div>
        )}
        
        {/* Camera name and time */}
        <div className="absolute bottom-0 left-0 right-0 p-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className={`font-semibold text-white ${sizeClasses[size]}`}>
                {camera.name}
              </h3>
              <p className="text-xs text-gray-400">{camera.location}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400 font-mono">
                {new Date().toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
        
        {/* Hover controls */}
        <div className={`
          absolute inset-0 flex items-center justify-center gap-2
          bg-black/40 backdrop-blur-sm
          transition-opacity duration-200
          ${isHovered ? 'opacity-100' : 'opacity-0'}
        `}>
          <button className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors">
            <Maximize2 size={20} className="text-white" />
          </button>
          <button className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors">
            <PictureInPicture size={20} className="text-white" />
          </button>
          <button className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors">
            <Download size={20} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
};

// Composant principal Multi-Camera View
const MultiCameraView = ({ cameras = [] }) => {
  const [layout, setLayout] = useState('2x2');
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [fullscreenCamera, setFullscreenCamera] = useState(null);
  const [showOverlays, setShowOverlays] = useState(true);
  const [showStats, setShowStats] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  
  const layoutConfig = LAYOUTS[layout];
  const camerasPerPage = layoutConfig.total;
  const totalPages = Math.ceil(cameras.length / camerasPerPage);
  const visibleCameras = cameras.slice(
    currentPage * camerasPerPage, 
    (currentPage + 1) * camerasPerPage
  );

  // Fullscreen mode
  if (fullscreenCamera) {
    const camera = cameras.find(c => c.id === fullscreenCamera);
    return (
      <div className="fixed inset-0 z-50 bg-black">
        <CameraFeed 
          camera={camera}
          isSelected={false}
          onSelect={() => {}}
          onDoubleClick={() => setFullscreenCamera(null)}
          showOverlay={showOverlays}
          showStats={showStats}
          size="large"
        />
        <button 
          onClick={() => setFullscreenCamera(null)}
          className="absolute top-4 right-4 p-3 rounded-full bg-white/20 hover:bg-white/30"
        >
          <Minimize2 size={24} className="text-white" />
        </button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-dark-900 rounded-2xl overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 bg-dark-800/50 backdrop-blur-sm border-b border-dark-700">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Camera className="text-primary" size={20} />
            Live View
          </h2>
          
          {/* Layout selector */}
          <div className="flex items-center gap-1 p-1 rounded-lg bg-dark-700">
            {Object.keys(LAYOUTS).map((key) => (
              <button
                key={key}
                onClick={() => setLayout(key)}
                className={`
                  px-3 py-1.5 rounded-md text-sm font-medium transition-all
                  ${layout === key 
                    ? 'bg-primary text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-dark-600'}
                `}
              >
                {key}
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Toggle overlays */}
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`
              p-2 rounded-lg transition-colors
              ${showOverlays ? 'bg-primary/20 text-primary' : 'bg-dark-700 text-gray-400'}
            `}
            title="Afficher les détections"
          >
            {showOverlays ? <Eye size={18} /> : <EyeOff size={18} />}
          </button>
          
          {/* Toggle stats */}
          <button
            onClick={() => setShowStats(!showStats)}
            className={`
              p-2 rounded-lg transition-colors
              ${showStats ? 'bg-primary/20 text-primary' : 'bg-dark-700 text-gray-400'}
            `}
            title="Afficher les compteurs"
          >
            <TrendingUp size={18} />
          </button>
          
          {/* Refresh */}
          <button className="p-2 rounded-lg bg-dark-700 text-gray-400 hover:text-white">
            <RefreshCw size={18} />
          </button>
          
          {/* Fullscreen all */}
          <button className="p-2 rounded-lg bg-dark-700 text-gray-400 hover:text-white">
            <Fullscreen size={18} />
          </button>
        </div>
      </div>
      
      {/* Camera Grid */}
      <div className="flex-1 p-4 overflow-hidden">
        <div 
          className="h-full grid gap-3"
          style={{
            gridTemplateColumns: `repeat(${layoutConfig.cols}, 1fr)`,
            gridTemplateRows: `repeat(${layoutConfig.rows}, 1fr)`,
          }}
        >
          {visibleCameras.map((camera) => (
            <CameraFeed
              key={camera.id}
              camera={camera}
              isSelected={selectedCamera === camera.id}
              onSelect={setSelectedCamera}
              onDoubleClick={setFullscreenCamera}
              showOverlay={showOverlays}
              showStats={showStats}
              size={layout === '4x4' ? 'small' : layout === '1x1' ? 'large' : 'normal'}
            />
          ))}
          
          {/* Empty slots */}
          {Array(Math.max(0, camerasPerPage - visibleCameras.length)).fill(null).map((_, i) => (
            <div 
              key={`empty-${i}`}
              className="rounded-xl bg-dark-800/50 border-2 border-dashed border-dark-600 flex items-center justify-center"
            >
              <div className="text-center text-gray-500">
                <Camera size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">Aucune caméra</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 p-4 bg-dark-800/50 border-t border-dark-700">
          <button
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
            className="p-2 rounded-lg bg-dark-700 text-gray-400 hover:text-white disabled:opacity-50"
          >
            <ChevronLeft size={20} />
          </button>
          
          <div className="flex items-center gap-2">
            {Array(totalPages).fill(null).map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentPage(i)}
                className={`
                  w-8 h-8 rounded-full text-sm font-medium transition-all
                  ${currentPage === i 
                    ? 'bg-primary text-white' 
                    : 'bg-dark-700 text-gray-400 hover:bg-dark-600'}
                `}
              >
                {i + 1}
              </button>
            ))}
          </div>
          
          <button
            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
            disabled={currentPage === totalPages - 1}
            className="p-2 rounded-lg bg-dark-700 text-gray-400 hover:text-white disabled:opacity-50"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      )}
    </div>
  );
};

export default MultiCameraView;
