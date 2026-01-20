/**
 * OhmVision - Video Timeline Player
 * Timeline de lecture vidéo avec replay, événements et navigation temporelle
 */

import React, { useState, useRef } from 'react';
import {
  Play, Pause, SkipBack, SkipForward, Rewind, FastForward,
  Volume2, VolumeX, Maximize2, Minimize2, Calendar, AlertTriangle, Users, Car, Flame,
  Download, Flag,
  Camera, Film, Scissors, Image
} from 'lucide-react';

// Event marker component on timeline
const EventMarker = ({ event, position, onClick, isSelected }) => {
  const eventColors = {
    person: 'bg-green-500',
    vehicle: 'bg-blue-500',
    fire: 'bg-red-500',
    intrusion: 'bg-orange-500',
    fall: 'bg-purple-500',
    ppe: 'bg-yellow-500',
    motion: 'bg-gray-400',
  };

  const eventIcons = {
    person: Users,
    vehicle: Car,
    fire: Flame,
    intrusion: AlertTriangle,
    fall: Users,
    ppe: AlertTriangle,
    motion: Camera,
  };

  const Icon = eventIcons[event.type] || AlertTriangle;

  return (
    <div
      className={`
        absolute top-0 transform -translate-x-1/2 cursor-pointer
        transition-all duration-200
        ${isSelected ? 'z-20 scale-125' : 'z-10 hover:scale-110'}
      `}
      style={{ left: `${position}%` }}
      onClick={() => onClick(event)}
    >
      <div className={`
        w-3 h-8 rounded-full flex items-center justify-center
        ${eventColors[event.type] || 'bg-gray-500'}
        ${isSelected ? 'ring-2 ring-white' : ''}
      `}>
        <div className="w-1.5 h-1.5 rounded-full bg-white" />
      </div>
      
      {/* Tooltip on hover */}
      <div className="
        absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2
        opacity-0 group-hover:opacity-100 transition-opacity
        pointer-events-none
      ">
        <div className="bg-dark-800 rounded-lg px-2 py-1 text-xs text-white whitespace-nowrap shadow-lg">
          <div className="flex items-center gap-1">
            <Icon size={10} />
            <span>{event.label}</span>
          </div>
          <span className="text-gray-400">{event.time}</span>
        </div>
      </div>
    </div>
  );
};

// Thumbnail preview component
const ThumbnailPreview = ({ time, position, visible }) => {
  if (!visible) return null;

  return (
    <div
      className="absolute bottom-full mb-4 transform -translate-x-1/2 pointer-events-none"
      style={{ left: `${position}%` }}
    >
      <div className="bg-dark-800 rounded-lg overflow-hidden shadow-2xl border border-dark-600">
        <div className="w-40 h-24 bg-dark-900 flex items-center justify-center">
          <Image size={24} className="text-gray-600" />
        </div>
        <div className="px-2 py-1 text-center">
          <span className="text-xs text-white font-mono">{time}</span>
        </div>
      </div>
    </div>
  );
};

// Time range selector
const TimeRangeSelector = ({ onChange }) => {
  const ranges = [
    { label: '1h', hours: 1 },
    { label: '4h', hours: 4 },
    { label: '12h', hours: 12 },
    { label: '24h', hours: 24 },
    { label: '48h', hours: 48 },
    { label: '7j', hours: 168 },
  ];

  const [selectedRange, setSelectedRange] = useState(24);

  return (
    <div className="flex items-center gap-1 p-1 rounded-lg bg-dark-700">
      {ranges.map((range) => (
        <button
          key={range.hours}
          onClick={() => {
            setSelectedRange(range.hours);
            onChange?.(range.hours);
          }}
          className={`
            px-2 py-1 rounded text-xs font-medium transition-all
            ${selectedRange === range.hours
              ? 'bg-primary text-white'
              : 'text-gray-400 hover:text-white'}
          `}
        >
          {range.label}
        </button>
      ))}
    </div>
  );
};

// Main Video Timeline Player Component
const VideoTimelinePlayer = ({
  videoUrl = null,
  cameraName = 'Caméra',
  events = [],
  recordings = [],
  onEventClick,
  onTimeChange,
  onExport,
}) => {
  const videoRef = useRef(null);
  const timelineRef = useRef(null);
  
  // Player state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(86400); // 24h in seconds
  const [_volume, _setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  
  // Timeline state
  const [_timelineZoom, _setTimelineZoom] = useState(1);
  const [_timelineOffset, _setTimelineOffset] = useState(0);
  const [_isDragging, _setIsDragging] = useState(false);
  const [hoverPosition, setHoverPosition] = useState(null);
  const [hoverTime, setHoverTime] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  
  // Date selection
  const [selectedDate, _setSelectedDate] = useState(new Date());

  // Format time helper
  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Handle play/pause
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
    }
    setIsPlaying(!isPlaying);
  };

  // Handle seek
  const handleSeek = (position) => {
    const newTime = (position / 100) * duration;
    setCurrentTime(newTime);
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
    }
    onTimeChange?.(newTime);
  };

  // Handle timeline click
  const handleTimelineClick = (e) => {
    const rect = timelineRef.current.getBoundingClientRect();
    const position = ((e.clientX - rect.left) / rect.width) * 100;
    handleSeek(position);
  };

  // Handle timeline hover
  const handleTimelineHover = (e) => {
    const rect = timelineRef.current.getBoundingClientRect();
    const position = ((e.clientX - rect.left) / rect.width) * 100;
    setHoverPosition(position);
    setHoverTime(formatTime((position / 100) * duration));
  };

  // Skip forward/backward
  const skip = (seconds) => {
    const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
    setCurrentTime(newTime);
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
    }
  };

  // Change playback speed
  const changeSpeed = () => {
    const speeds = [0.5, 1, 1.5, 2, 4, 8];
    const currentIndex = speeds.indexOf(playbackSpeed);
    const nextIndex = (currentIndex + 1) % speeds.length;
    setPlaybackSpeed(speeds[nextIndex]);
    if (videoRef.current) {
      videoRef.current.playbackRate = speeds[nextIndex];
    }
  };

  // Toggle fullscreen
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Generate timeline hours
  const timelineHours = Array.from({ length: 25 }, (_, i) => i);

  // Calculate current position percentage
  const currentPosition = (currentTime / duration) * 100;

  return (
    <div className="h-full flex flex-col bg-dark-900 rounded-2xl overflow-hidden">
      {/* Video Area */}
      <div className="relative flex-1 bg-black min-h-0">
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            className="w-full h-full object-contain"
            onTimeUpdate={(e) => setCurrentTime(e.target.currentTime)}
            onLoadedMetadata={(e) => setDuration(e.target.duration)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center text-gray-500">
              <Film size={64} className="mx-auto mb-4 opacity-30" />
              <p className="text-lg">Sélectionnez une période</p>
              <p className="text-sm">pour charger l'enregistrement</p>
            </div>
          </div>
        )}

        {/* Video overlay controls */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity bg-black/30">
          <button
            onClick={togglePlay}
            className="p-6 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all"
          >
            {isPlaying ? <Pause size={48} /> : <Play size={48} />}
          </button>
        </div>

        {/* Camera info overlay */}
        <div className="absolute top-4 left-4 flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-black/60 backdrop-blur-sm">
            <span className="text-sm font-medium text-white">{cameraName}</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-black/60 backdrop-blur-sm">
            <span className="text-sm font-mono text-white">
              {selectedDate.toLocaleDateString('fr-FR')} {formatTime(currentTime)}
            </span>
          </div>
        </div>

        {/* Speed indicator */}
        {playbackSpeed !== 1 && (
          <div className="absolute top-4 right-4 px-3 py-1.5 rounded-lg bg-primary/80 backdrop-blur-sm">
            <span className="text-sm font-bold text-white">{playbackSpeed}x</span>
          </div>
        )}
      </div>

      {/* Controls Bar */}
      <div className="p-4 bg-dark-800/50 backdrop-blur-sm border-t border-dark-700">
        {/* Timeline */}
        <div className="mb-4">
          <div
            ref={timelineRef}
            className="relative h-12 bg-dark-700 rounded-lg cursor-pointer overflow-hidden"
            onClick={handleTimelineClick}
            onMouseMove={handleTimelineHover}
            onMouseLeave={() => setHoverPosition(null)}
          >
            {/* Recording segments */}
            {recordings.map((rec, index) => (
              <div
                key={index}
                className="absolute top-0 h-full bg-primary/30"
                style={{
                  left: `${(rec.start / duration) * 100}%`,
                  width: `${((rec.end - rec.start) / duration) * 100}%`,
                }}
              />
            ))}

            {/* Hour markers */}
            <div className="absolute inset-0 flex">
              {timelineHours.map((hour) => (
                <div
                  key={hour}
                  className="flex-1 border-r border-dark-600 relative"
                >
                  <span className="absolute bottom-1 left-1 text-[10px] text-gray-500">
                    {hour.toString().padStart(2, '0')}:00
                  </span>
                </div>
              ))}
            </div>

            {/* Event markers */}
            {events.map((event, index) => (
              <EventMarker
                key={index}
                event={event}
                position={(event.timestamp / duration) * 100}
                onClick={(e) => {
                  setSelectedEvent(e);
                  handleSeek((e.timestamp / duration) * 100);
                  onEventClick?.(e);
                }}
                isSelected={selectedEvent?.id === event.id}
              />
            ))}

            {/* Progress bar */}
            <div
              className="absolute top-0 left-0 h-full bg-primary/50"
              style={{ width: `${currentPosition}%` }}
            />

            {/* Playhead */}
            <div
              className="absolute top-0 w-0.5 h-full bg-white shadow-lg"
              style={{ left: `${currentPosition}%` }}
            >
              <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-white rounded-full shadow-lg" />
            </div>

            {/* Hover preview */}
            <ThumbnailPreview
              time={hoverTime}
              position={hoverPosition}
              visible={hoverPosition !== null}
            />
          </div>
        </div>

        {/* Control buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Date picker */}
            <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors">
              <Calendar size={16} className="text-gray-400" />
              <span className="text-sm text-white">
                {selectedDate.toLocaleDateString('fr-FR')}
              </span>
            </button>

            {/* Time range selector */}
            <TimeRangeSelector onChange={(hours) => setDuration(hours * 3600)} />
          </div>

          <div className="flex items-center gap-2">
            {/* Skip backward */}
            <button
              onClick={() => skip(-60)}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
              title="-1 min"
            >
              <SkipBack size={18} />
            </button>

            {/* Rewind */}
            <button
              onClick={() => skip(-10)}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
              title="-10 sec"
            >
              <Rewind size={18} />
            </button>

            {/* Play/Pause */}
            <button
              onClick={togglePlay}
              className="p-3 rounded-xl bg-primary hover:bg-primary/80 text-white transition-colors"
            >
              {isPlaying ? <Pause size={20} /> : <Play size={20} />}
            </button>

            {/* Fast forward */}
            <button
              onClick={() => skip(10)}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
              title="+10 sec"
            >
              <FastForward size={18} />
            </button>

            {/* Skip forward */}
            <button
              onClick={() => skip(60)}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
              title="+1 min"
            >
              <SkipForward size={18} />
            </button>

            {/* Speed control */}
            <button
              onClick={changeSpeed}
              className="px-3 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-sm font-medium text-gray-400 hover:text-white transition-colors min-w-[48px]"
            >
              {playbackSpeed}x
            </button>
          </div>

          <div className="flex items-center gap-2">
            {/* Current time display */}
            <div className="px-3 py-2 rounded-lg bg-dark-700">
              <span className="text-sm font-mono text-white">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>

            {/* Volume */}
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
            >
              {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
            </button>

            {/* Export clip */}
            <button
              onClick={onExport}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
              title="Exporter le clip"
            >
              <Scissors size={18} />
            </button>

            {/* Download */}
            <button
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
              title="Télécharger"
            >
              <Download size={18} />
            </button>

            {/* Fullscreen */}
            <button
              onClick={toggleFullscreen}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white transition-colors"
            >
              {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </button>
          </div>
        </div>
      </div>

      {/* Events panel (collapsible) */}
      <div className="border-t border-dark-700">
        <div className="p-3 bg-dark-800/30">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <Flag size={14} className="text-primary" />
              Événements ({events.length})
            </h4>
            <button className="text-xs text-primary hover:underline">
              Filtrer
            </button>
          </div>

          <div className="flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
            {events.slice(0, 10).map((event, index) => (
              <button
                key={index}
                onClick={() => {
                  setSelectedEvent(event);
                  handleSeek((event.timestamp / duration) * 100);
                }}
                className={`
                  flex-shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg
                  transition-all
                  ${selectedEvent?.id === event.id
                    ? 'bg-primary text-white'
                    : 'bg-dark-700 text-gray-300 hover:bg-dark-600'}
                `}
              >
                <AlertTriangle size={12} />
                <span className="text-xs whitespace-nowrap">{event.label}</span>
                <span className="text-[10px] opacity-70">{event.time}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoTimelinePlayer;
