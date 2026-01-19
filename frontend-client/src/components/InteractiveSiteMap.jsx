/**
 * OhmVision - Interactive Site Map
 * Plan interactif du site avec positions des caméras et alertes en temps réel
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Camera, AlertTriangle, Users, Car, Flame, Shield, ZoomIn, ZoomOut,
  Move, Layers, Eye, EyeOff, MapPin, Navigation, Maximize2, RefreshCw,
  Circle, Square, Triangle, Hexagon, Plus, Minus, RotateCcw, Settings,
  Play, Pause, ChevronLeft, ChevronRight
} from 'lucide-react';

// Camera marker component
const CameraMarker = ({ 
  camera, 
  isSelected, 
  onClick, 
  scale = 1,
  showLabel = true,
  showStats = true 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-red-500',
    warning: 'bg-orange-500',
    recording: 'bg-red-500 animate-pulse',
  };

  const statusGlow = {
    online: 'shadow-green-500/50',
    offline: 'shadow-red-500/50',
    warning: 'shadow-orange-500/50',
    recording: 'shadow-red-500/50',
  };

  return (
    <div
      className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
      style={{ 
        left: `${camera.x}%`, 
        top: `${camera.y}%`,
        zIndex: isSelected || isHovered ? 100 : 10
      }}
      onClick={() => onClick(camera)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Field of view cone */}
      {(isSelected || isHovered) && (
        <div 
          className="absolute w-32 h-32 opacity-20"
          style={{
            transform: `rotate(${camera.rotation || 0}deg)`,
            background: `conic-gradient(from -30deg, transparent 0deg, rgba(99, 102, 241, 0.5) 30deg, rgba(99, 102, 241, 0.5) 60deg, transparent 60deg)`,
            transformOrigin: 'center center',
            left: '-50%',
            top: '-50%',
          }}
        />
      )}
      
      {/* Camera icon */}
      <div className={`
        relative p-2 rounded-full 
        ${isSelected ? 'bg-primary ring-4 ring-primary/30' : 'bg-dark-700'}
        ${statusGlow[camera.status]} shadow-lg
        transition-all duration-300
        ${isHovered ? 'scale-125' : ''}
      `}>
        <Camera size={16 * scale} className="text-white" />
        
        {/* Status indicator */}
        <div className={`
          absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-dark-900
          ${statusColors[camera.status]}
        `} />
        
        {/* Alert badge */}
        {camera.alertCount > 0 && (
          <div className="absolute -top-2 -left-2 w-5 h-5 rounded-full bg-red-500 flex items-center justify-center">
            <span className="text-[10px] font-bold text-white">{camera.alertCount}</span>
          </div>
        )}
      </div>
      
      {/* Stats popup */}
      {showStats && (isSelected || isHovered) && (
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 z-50">
          <div className="bg-dark-800/95 backdrop-blur-xl rounded-xl p-3 border border-dark-600 shadow-2xl min-w-[180px]">
            <p className="font-semibold text-white text-sm mb-2">{camera.name}</p>
            
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400 flex items-center gap-1">
                  <Users size={12} /> Personnes
                </span>
                <span className="text-green-400 font-mono">{camera.persons || 0}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400 flex items-center gap-1">
                  <Car size={12} /> Véhicules
                </span>
                <span className="text-blue-400 font-mono">{camera.vehicles || 0}</span>
              </div>
              {camera.temperature && (
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">🌡️ Temp.</span>
                  <span className="text-orange-400 font-mono">{camera.temperature}°C</span>
                </div>
              )}
            </div>
            
            <div className="mt-2 pt-2 border-t border-dark-600">
              <button className="w-full text-xs text-primary hover:text-primary/80 flex items-center justify-center gap-1">
                <Eye size={12} /> Voir en direct
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Label */}
      {showLabel && !isHovered && (
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1">
          <span className="text-[10px] text-gray-400 whitespace-nowrap bg-dark-900/80 px-1.5 py-0.5 rounded">
            {camera.name}
          </span>
        </div>
      )}
    </div>
  );
};

// Zone overlay component
const ZoneOverlay = ({ zone, isSelected, onClick }) => {
  const zoneColors = {
    restricted: 'border-red-500 bg-red-500/10',
    monitored: 'border-blue-500 bg-blue-500/10',
    counting: 'border-green-500 bg-green-500/10',
    parking: 'border-purple-500 bg-purple-500/10',
  };

  return (
    <div
      className={`
        absolute border-2 border-dashed rounded-lg cursor-pointer
        transition-all duration-300
        ${zoneColors[zone.type] || 'border-gray-500 bg-gray-500/10'}
        ${isSelected ? 'ring-2 ring-white/50' : ''}
        hover:bg-opacity-20
      `}
      style={{
        left: `${zone.x}%`,
        top: `${zone.y}%`,
        width: `${zone.width}%`,
        height: `${zone.height}%`,
      }}
      onClick={() => onClick(zone)}
    >
      <div className="absolute -top-6 left-0 text-xs text-gray-400 whitespace-nowrap">
        {zone.name}
      </div>
      
      {zone.count !== undefined && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-white/50">{zone.count}</span>
        </div>
      )}
    </div>
  );
};

// Alert marker component
const AlertMarker = ({ alert }) => (
  <div
    className="absolute transform -translate-x-1/2 -translate-y-1/2 animate-ping"
    style={{ left: `${alert.x}%`, top: `${alert.y}%` }}
  >
    <div className="w-8 h-8 rounded-full bg-red-500/30 flex items-center justify-center">
      <AlertTriangle size={16} className="text-red-500" />
    </div>
  </div>
);

// Heatmap overlay
const HeatmapOverlay = ({ data, opacity = 0.5 }) => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw heatmap points
    data.forEach(point => {
      const x = (point.x / 100) * width;
      const y = (point.y / 100) * height;
      const intensity = point.intensity || 0.5;
      
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, 30);
      gradient.addColorStop(0, `rgba(255, 0, 0, ${intensity})`);
      gradient.addColorStop(0.5, `rgba(255, 255, 0, ${intensity * 0.5})`);
      gradient.addColorStop(1, 'rgba(0, 0, 255, 0)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x - 30, y - 30, 60, 60);
    });
  }, [data]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={600}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ opacity }}
    />
  );
};

// Main Interactive Site Map Component
const InteractiveSiteMap = ({ 
  floorPlan = null, // URL or base64 of floor plan image
  cameras = [],
  zones = [],
  alerts = [],
  heatmapData = null,
  onCameraSelect,
  onZoneSelect,
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null);
  
  // Layer visibility
  const [showCameras, setShowCameras] = useState(true);
  const [showZones, setShowZones] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showLabels, setShowLabels] = useState(true);
  const [showAlerts, setShowAlerts] = useState(true);
  
  const mapRef = useRef(null);

  // Handle zoom
  const handleZoom = (delta) => {
    setZoom(prev => Math.min(Math.max(prev + delta, 0.5), 3));
  };

  // Handle pan
  const handleMouseDown = (e) => {
    if (e.button === 0) { // Left click
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Handle wheel zoom
  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    handleZoom(delta);
  };

  // Reset view
  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Handle camera click
  const handleCameraClick = (camera) => {
    setSelectedCamera(camera.id === selectedCamera ? null : camera.id);
    onCameraSelect?.(camera);
  };

  // Handle zone click
  const handleZoneClick = (zone) => {
    setSelectedZone(zone.id === selectedZone ? null : zone.id);
    onZoneSelect?.(zone);
  };

  // Mock floor plan if none provided
  const defaultFloorPlan = `data:image/svg+xml,${encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
      <rect fill="#1a1a2e" width="800" height="600"/>
      <rect fill="#16213e" x="50" y="50" width="300" height="200" rx="5"/>
      <text fill="#4a5568" x="200" y="150" text-anchor="middle" font-size="14">Bâtiment A</text>
      <rect fill="#16213e" x="450" y="50" width="300" height="200" rx="5"/>
      <text fill="#4a5568" x="600" y="150" text-anchor="middle" font-size="14">Bâtiment B</text>
      <rect fill="#16213e" x="50" y="350" width="700" height="200" rx="5"/>
      <text fill="#4a5568" x="400" y="450" text-anchor="middle" font-size="14">Parking</text>
      <rect fill="#0f3460" x="360" y="250" width="80" height="100" rx="5"/>
      <text fill="#4a5568" x="400" y="310" text-anchor="middle" font-size="12">Entrée</text>
    </svg>
  `)}`;

  return (
    <div className="h-full flex flex-col bg-dark-900 rounded-2xl overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 bg-dark-800/50 backdrop-blur-sm border-b border-dark-700">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <MapPin size={16} className="text-primary" />
            Plan du site
          </h3>
          
          {/* Floor selector (if multi-floor) */}
          <div className="hidden md:flex items-center gap-1 ml-4 p-1 rounded-lg bg-dark-700">
            <button className="px-2 py-1 text-xs rounded bg-primary text-white">RDC</button>
            <button className="px-2 py-1 text-xs rounded text-gray-400 hover:text-white">Étage 1</button>
            <button className="px-2 py-1 text-xs rounded text-gray-400 hover:text-white">Étage 2</button>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Layer toggles */}
          <div className="hidden md:flex items-center gap-1 p-1 rounded-lg bg-dark-700">
            <button
              onClick={() => setShowCameras(!showCameras)}
              className={`p-1.5 rounded ${showCameras ? 'bg-primary/20 text-primary' : 'text-gray-400'}`}
              title="Caméras"
            >
              <Camera size={14} />
            </button>
            <button
              onClick={() => setShowZones(!showZones)}
              className={`p-1.5 rounded ${showZones ? 'bg-primary/20 text-primary' : 'text-gray-400'}`}
              title="Zones"
            >
              <Square size={14} />
            </button>
            <button
              onClick={() => setShowHeatmap(!showHeatmap)}
              className={`p-1.5 rounded ${showHeatmap ? 'bg-primary/20 text-primary' : 'text-gray-400'}`}
              title="Heatmap"
            >
              <Layers size={14} />
            </button>
            <button
              onClick={() => setShowLabels(!showLabels)}
              className={`p-1.5 rounded ${showLabels ? 'bg-primary/20 text-primary' : 'text-gray-400'}`}
              title="Labels"
            >
              {showLabels ? <Eye size={14} /> : <EyeOff size={14} />}
            </button>
            <button
              onClick={() => setShowAlerts(!showAlerts)}
              className={`p-1.5 rounded ${showAlerts ? 'bg-primary/20 text-primary' : 'text-gray-400'}`}
              title="Alertes"
            >
              <AlertTriangle size={14} />
            </button>
          </div>
          
          {/* Zoom controls */}
          <div className="flex items-center gap-1 p-1 rounded-lg bg-dark-700">
            <button
              onClick={() => handleZoom(-0.2)}
              className="p-1.5 rounded text-gray-400 hover:text-white"
            >
              <ZoomOut size={14} />
            </button>
            <span className="text-xs text-gray-400 w-12 text-center">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={() => handleZoom(0.2)}
              className="p-1.5 rounded text-gray-400 hover:text-white"
            >
              <ZoomIn size={14} />
            </button>
          </div>
          
          <button
            onClick={resetView}
            className="p-2 rounded-lg bg-dark-700 text-gray-400 hover:text-white"
            title="Réinitialiser"
          >
            <RotateCcw size={14} />
          </button>
          
          <button className="p-2 rounded-lg bg-dark-700 text-gray-400 hover:text-white">
            <Maximize2 size={14} />
          </button>
        </div>
      </div>
      
      {/* Map area */}
      <div 
        ref={mapRef}
        className="flex-1 relative overflow-hidden cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        <div
          className="absolute inset-0 transition-transform duration-100"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center'
          }}
        >
          {/* Floor plan image */}
          <img
            src={floorPlan || defaultFloorPlan}
            alt="Plan du site"
            className="w-full h-full object-contain"
            draggable={false}
          />
          
          {/* Heatmap layer */}
          {showHeatmap && heatmapData && (
            <HeatmapOverlay data={heatmapData} opacity={0.4} />
          )}
          
          {/* Zones layer */}
          {showZones && zones.map(zone => (
            <ZoneOverlay
              key={zone.id}
              zone={zone}
              isSelected={selectedZone === zone.id}
              onClick={handleZoneClick}
            />
          ))}
          
          {/* Alerts layer */}
          {showAlerts && alerts.map((alert, index) => (
            <AlertMarker key={index} alert={alert} />
          ))}
          
          {/* Cameras layer */}
          {showCameras && cameras.map(camera => (
            <CameraMarker
              key={camera.id}
              camera={camera}
              isSelected={selectedCamera === camera.id}
              onClick={handleCameraClick}
              scale={1 / zoom}
              showLabel={showLabels}
              showStats={true}
            />
          ))}
        </div>
        
        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-dark-800/90 backdrop-blur-sm rounded-xl p-3 border border-dark-700">
          <p className="text-xs font-semibold text-gray-400 mb-2">Légende</p>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-gray-300">En ligne</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-gray-300">Hors ligne</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="text-gray-300">Alerte</span>
            </div>
          </div>
        </div>
        
        {/* Mini stats panel */}
        <div className="absolute top-4 right-4 bg-dark-800/90 backdrop-blur-sm rounded-xl p-3 border border-dark-700">
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center">
              <p className="text-lg font-bold text-green-400">{cameras.filter(c => c.status === 'online').length}</p>
              <p className="text-[10px] text-gray-400">En ligne</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-red-400">{cameras.filter(c => c.status === 'offline').length}</p>
              <p className="text-[10px] text-gray-400">Hors ligne</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-blue-400">{zones.length}</p>
              <p className="text-[10px] text-gray-400">Zones</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-orange-400">{alerts.length}</p>
              <p className="text-[10px] text-gray-400">Alertes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveSiteMap;
