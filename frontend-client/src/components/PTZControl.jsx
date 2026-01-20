/**
 * OhmVision - PTZ Control & Digital Zoom
 * Contrôle PTZ (Pan-Tilt-Zoom) et zoom numérique avancé
 */

import React, { useState, useRef } from 'react';
import {
  ZoomIn, ZoomOut, RotateCcw,
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Home,
  Focus, Aperture, Sun, Camera, Save, Grid, Crosshair, Target, Sliders
} from 'lucide-react';

// Digital zoom viewer with pan
const DigitalZoomViewer = ({
  imageSrc,
  zoom = 1,
  pan = { x: 0, y: 0 },
  onZoomChange,
  onPanChange,
  showGrid = false,
  showCrosshair = false,
}) => {
  const containerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    if (zoom > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging && zoom > 1) {
      const newPan = {
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      };
      onPanChange?.(newPan);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    const newZoom = Math.max(1, Math.min(8, zoom + delta));
    onZoomChange?.(newZoom);
  };

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-full overflow-hidden bg-black ${zoom > 1 ? 'cursor-grab active:cursor-grabbing' : ''}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      <div
        className="w-full h-full transition-transform duration-100"
        style={{
          transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
          transformOrigin: 'center center',
        }}
      >
        <img
          src={imageSrc}
          alt="Camera feed"
          className="w-full h-full object-contain"
          draggable={false}
        />
      </div>

      {/* Grid overlay */}
      {showGrid && (
        <div className="absolute inset-0 pointer-events-none">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="10%" height="10%" patternUnits="userSpaceOnUse">
                <path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
      )}

      {/* Crosshair overlay */}
      {showCrosshair && (
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
          <div className="relative">
            <div className="absolute w-20 h-0.5 bg-red-500/50 -translate-x-1/2" />
            <div className="absolute h-20 w-0.5 bg-red-500/50 -translate-y-1/2" />
            <div className="w-8 h-8 border-2 border-red-500/50 rounded-full" />
          </div>
        </div>
      )}

      {/* Zoom indicator */}
      <div className="absolute bottom-4 right-4 px-2 py-1 rounded bg-black/60 backdrop-blur-sm">
        <span className="text-sm font-mono text-white">{zoom.toFixed(1)}x</span>
      </div>

      {/* Mini map (when zoomed) */}
      {zoom > 1.5 && (
        <div className="absolute top-4 right-4 w-32 h-24 bg-black/60 backdrop-blur-sm rounded-lg overflow-hidden border border-white/20">
          <img
            src={imageSrc}
            alt="Mini map"
            className="w-full h-full object-contain opacity-50"
          />
          <div
            className="absolute border-2 border-primary"
            style={{
              width: `${100 / zoom}%`,
              height: `${100 / zoom}%`,
              left: `${50 - (pan.x / zoom) / 2}%`,
              top: `${50 - (pan.y / zoom) / 2}%`,
              transform: 'translate(-50%, -50%)',
            }}
          />
        </div>
      )}
    </div>
  );
};

// PTZ direction pad component
const PTZDirectionPad = ({ onMove, onStop, disabled = false }) => {
  const [activeDirection, setActiveDirection] = useState(null);
  const intervalRef = useRef(null);

  const startMove = (direction) => {
    if (disabled) return;
    setActiveDirection(direction);
    onMove?.(direction);
    
    // Continuous movement while pressed
    intervalRef.current = setInterval(() => {
      onMove?.(direction);
    }, 100);
  };

  const stopMove = () => {
    setActiveDirection(null);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    onStop?.();
  };

  const directions = [
    { id: 'up', icon: ChevronUp, row: 1, col: 2 },
    { id: 'down', icon: ChevronDown, row: 3, col: 2 },
    { id: 'left', icon: ChevronLeft, row: 2, col: 1 },
    { id: 'right', icon: ChevronRight, row: 2, col: 3 },
    { id: 'up-left', icon: ChevronUp, row: 1, col: 1, rotate: -45 },
    { id: 'up-right', icon: ChevronUp, row: 1, col: 3, rotate: 45 },
    { id: 'down-left', icon: ChevronDown, row: 3, col: 1, rotate: 45 },
    { id: 'down-right', icon: ChevronDown, row: 3, col: 3, rotate: -45 },
  ];

  return (
    <div className="relative w-32 h-32">
      {/* Background circle */}
      <div className="absolute inset-0 rounded-full bg-dark-700 border border-dark-600" />
      
      {/* Direction buttons */}
      <div className="absolute inset-2 grid grid-cols-3 grid-rows-3 gap-0.5">
        {directions.map((dir) => {
          const Icon = dir.icon;
          return (
            <button
              key={dir.id}
              className={`
                flex items-center justify-center rounded-lg transition-all
                ${activeDirection === dir.id ? 'bg-primary text-white' : 'hover:bg-dark-600 text-gray-400'}
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              style={{
                gridRow: dir.row,
                gridColumn: dir.col,
              }}
              onMouseDown={() => startMove(dir.id)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(dir.id)}
              onTouchEnd={stopMove}
              disabled={disabled}
            >
              <Icon 
                size={16} 
                style={{ transform: dir.rotate ? `rotate(${dir.rotate}deg)` : undefined }}
              />
            </button>
          );
        })}
        
        {/* Center home button */}
        <button
          className={`
            flex items-center justify-center rounded-lg transition-all
            hover:bg-primary text-gray-400 hover:text-white
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          style={{ gridRow: 2, gridColumn: 2 }}
          onClick={() => onMove?.('home')}
          disabled={disabled}
        >
          <Home size={16} />
        </button>
      </div>
    </div>
  );
};

// Zoom slider component
const ZoomSlider = ({ value, min = 1, max = 8, onChange, disabled = false }) => {
  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={() => onChange?.(Math.min(max, value + 0.5))}
        className={`p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors ${disabled ? 'opacity-50' : ''}`}
        disabled={disabled}
      >
        <ZoomIn size={18} />
      </button>
      
      <div className="relative h-32 w-8 bg-dark-700 rounded-full overflow-hidden">
        <div
          className="absolute bottom-0 left-0 right-0 bg-primary transition-all"
          style={{ height: `${((value - min) / (max - min)) * 100}%` }}
        />
        <input
          type="range"
          min={min}
          max={max}
          step={0.1}
          value={value}
          onChange={(e) => onChange?.(parseFloat(e.target.value))}
          className="absolute inset-0 opacity-0 cursor-pointer"
          style={{ writingMode: 'bt-lr', WebkitAppearance: 'slider-vertical' }}
          disabled={disabled}
        />
      </div>
      
      <button
        onClick={() => onChange?.(Math.max(min, value - 0.5))}
        className={`p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors ${disabled ? 'opacity-50' : ''}`}
        disabled={disabled}
      >
        <ZoomOut size={18} />
      </button>
      
      <span className="text-xs text-gray-400 font-mono">{value.toFixed(1)}x</span>
    </div>
  );
};

// Preset buttons
const PresetButtons = ({ presets, onSelect, onSave, currentPreset }) => {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-400">Préréglages</span>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="text-xs text-primary hover:underline"
        >
          {isEditing ? 'Terminé' : 'Modifier'}
        </button>
      </div>
      
      <div className="grid grid-cols-4 gap-1">
        {presets.map((preset) => (
          <button
            key={preset.id}
            onClick={() => isEditing ? onSave?.(preset.id) : onSelect?.(preset)}
            className={`
              p-2 rounded-lg text-xs font-medium transition-all
              ${currentPreset === preset.id
                ? 'bg-primary text-white'
                : 'bg-dark-700 text-gray-400 hover:bg-dark-600 hover:text-white'}
              ${isEditing ? 'ring-2 ring-orange-500/50' : ''}
            `}
          >
            {isEditing ? <Save size={12} /> : preset.name}
          </button>
        ))}
      </div>
    </div>
  );
};

// Advanced camera controls
const AdvancedControls = ({ onFocus, onIris, onBrightness, disabled = false }) => {
  const [focusValue, setFocusValue] = useState(50);
  const [irisValue, setIrisValue] = useState(50);
  const [brightnessValue, setBrightnessValue] = useState(50);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Focus size={14} className="text-gray-400" />
        <span className="text-xs text-gray-400 w-16">Focus</span>
        <input
          type="range"
          min={0}
          max={100}
          value={focusValue}
          onChange={(e) => {
            setFocusValue(parseInt(e.target.value));
            onFocus?.(parseInt(e.target.value));
          }}
          className="flex-1 h-1 bg-dark-600 rounded-full appearance-none cursor-pointer"
          disabled={disabled}
        />
      </div>
      
      <div className="flex items-center gap-2">
        <Aperture size={14} className="text-gray-400" />
        <span className="text-xs text-gray-400 w-16">Iris</span>
        <input
          type="range"
          min={0}
          max={100}
          value={irisValue}
          onChange={(e) => {
            setIrisValue(parseInt(e.target.value));
            onIris?.(parseInt(e.target.value));
          }}
          className="flex-1 h-1 bg-dark-600 rounded-full appearance-none cursor-pointer"
          disabled={disabled}
        />
      </div>
      
      <div className="flex items-center gap-2">
        <Sun size={14} className="text-gray-400" />
        <span className="text-xs text-gray-400 w-16">Lumino.</span>
        <input
          type="range"
          min={0}
          max={100}
          value={brightnessValue}
          onChange={(e) => {
            setBrightnessValue(parseInt(e.target.value));
            onBrightness?.(parseInt(e.target.value));
          }}
          className="flex-1 h-1 bg-dark-600 rounded-full appearance-none cursor-pointer"
          disabled={disabled}
        />
      </div>
    </div>
  );
};

// Main PTZ Control Component
const PTZControl = ({
  cameraId,
  imageSrc = '/api/streaming/snapshot/1',
  hasPTZ = true,
  hasDigitalZoom = true,
  onPTZMove,
  onPTZStop,
  onPresetSelect,
  onPresetSave,
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [showGrid, setShowGrid] = useState(false);
  const [showCrosshair, setShowCrosshair] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isPTZMode, setIsPTZMode] = useState(hasPTZ);

  const presets = [
    { id: 1, name: 'P1', pan: 0, tilt: 0, zoom: 1 },
    { id: 2, name: 'P2', pan: 45, tilt: 10, zoom: 2 },
    { id: 3, name: 'P3', pan: -45, tilt: 0, zoom: 1.5 },
    { id: 4, name: 'P4', pan: 90, tilt: -10, zoom: 3 },
    { id: 5, name: 'P5', pan: -90, tilt: 20, zoom: 2 },
    { id: 6, name: 'P6', pan: 180, tilt: 0, zoom: 1 },
    { id: 7, name: 'P7', pan: 0, tilt: 45, zoom: 4 },
    { id: 8, name: 'P8', pan: 0, tilt: -45, zoom: 1 },
  ];

  const handlePTZMove = (direction) => {
    console.log('PTZ Move:', direction);
    onPTZMove?.(cameraId, direction);
  };

  const handlePTZStop = () => {
    console.log('PTZ Stop');
    onPTZStop?.(cameraId);
  };

  const resetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="h-full flex bg-dark-900 rounded-2xl overflow-hidden">
      {/* Video area */}
      <div className="flex-1 relative">
        <DigitalZoomViewer
          imageSrc={imageSrc}
          zoom={zoom}
          pan={pan}
          onZoomChange={setZoom}
          onPanChange={setPan}
          showGrid={showGrid}
          showCrosshair={showCrosshair}
        />

        {/* Toolbar overlay */}
        <div className="absolute top-4 left-4 flex items-center gap-2">
          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`p-2 rounded-lg transition-colors ${showGrid ? 'bg-primary text-white' : 'bg-black/60 text-gray-400 hover:text-white'}`}
          >
            <Grid size={16} />
          </button>
          <button
            onClick={() => setShowCrosshair(!showCrosshair)}
            className={`p-2 rounded-lg transition-colors ${showCrosshair ? 'bg-primary text-white' : 'bg-black/60 text-gray-400 hover:text-white'}`}
          >
            <Crosshair size={16} />
          </button>
          <button
            onClick={resetZoom}
            className="p-2 rounded-lg bg-black/60 text-gray-400 hover:text-white transition-colors"
          >
            <RotateCcw size={16} />
          </button>
        </div>

        {/* Mode toggle */}
        {hasPTZ && hasDigitalZoom && (
          <div className="absolute bottom-4 left-4 flex items-center p-1 rounded-lg bg-black/60 backdrop-blur-sm">
            <button
              onClick={() => setIsPTZMode(true)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${isPTZMode ? 'bg-primary text-white' : 'text-gray-400'}`}
            >
              PTZ
            </button>
            <button
              onClick={() => setIsPTZMode(false)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${!isPTZMode ? 'bg-primary text-white' : 'text-gray-400'}`}
            >
              Numérique
            </button>
          </div>
        )}
      </div>

      {/* Control panel */}
      <div className="w-64 bg-dark-800/50 backdrop-blur-sm border-l border-dark-700 p-4 space-y-6 overflow-y-auto">
        <div className="text-center">
          <h3 className="text-sm font-semibold text-white mb-1">
            {isPTZMode ? 'Contrôle PTZ' : 'Zoom Numérique'}
          </h3>
          <p className="text-xs text-gray-400">
            {isPTZMode ? 'Mouvement caméra' : 'Zoom et déplacement'}
          </p>
        </div>

        {/* Direction pad or zoom controls */}
        <div className="flex justify-center gap-4">
          {isPTZMode ? (
            <PTZDirectionPad
              onMove={handlePTZMove}
              onStop={handlePTZStop}
              disabled={!hasPTZ}
            />
          ) : (
            <div className="flex gap-4">
              <ZoomSlider
                value={zoom}
                min={1}
                max={8}
                onChange={setZoom}
              />
              <div className="flex flex-col items-center justify-center gap-2">
                <button
                  onClick={resetZoom}
                  className="p-3 rounded-xl bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
                >
                  <Home size={20} />
                </button>
                <span className="text-[10px] text-gray-500">Reset</span>
              </div>
            </div>
          )}
        </div>

        {/* PTZ Zoom slider (only in PTZ mode) */}
        {isPTZMode && (
          <div className="flex items-center gap-3">
            <ZoomOut size={14} className="text-gray-400" />
            <input
              type="range"
              min={1}
              max={20}
              value={zoom}
              onChange={(e) => setZoom(parseFloat(e.target.value))}
              className="flex-1 h-1 bg-dark-600 rounded-full appearance-none cursor-pointer"
            />
            <ZoomIn size={14} className="text-gray-400" />
          </div>
        )}

        {/* Presets */}
        {isPTZMode && (
          <PresetButtons
            presets={presets}
            onSelect={(preset) => {
              onPresetSelect?.(cameraId, preset);
            }}
            onSave={(presetId) => {
              onPresetSave?.(cameraId, presetId);
            }}
          />
        )}

        {/* Advanced controls toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-between p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
        >
          <span className="text-xs text-gray-400 flex items-center gap-2">
            <Sliders size={14} />
            Paramètres avancés
          </span>
          <ChevronRight 
            size={14} 
            className={`text-gray-400 transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
          />
        </button>

        {/* Advanced controls */}
        {showAdvanced && (
          <AdvancedControls
            disabled={!hasPTZ}
          />
        )}

        {/* Quick actions */}
        <div className="pt-4 border-t border-dark-700 space-y-2">
          <button className="w-full flex items-center justify-center gap-2 p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors">
            <Camera size={14} />
            <span className="text-xs">Capturer image</span>
          </button>
          <button className="w-full flex items-center justify-center gap-2 p-2 rounded-lg bg-primary/20 hover:bg-primary/30 text-primary transition-colors">
            <Target size={14} />
            <span className="text-xs">Auto-tracking</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PTZControl;
