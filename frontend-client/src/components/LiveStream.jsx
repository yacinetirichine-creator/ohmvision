/**
 * OhmVision - LiveStream Component
 * Composant de streaming vidéo MJPEG
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Camera, WifiOff, RefreshCw, Loader } from 'lucide-react';
import { apiUrl } from '../services/apiBase';

/**
 * Composant d'affichage du flux vidéo en direct
 * 
 * @param {Object} props
 * @param {number} props.cameraId - ID de la caméra
 * @param {string} props.rtspUrl - URL RTSP de la caméra (pour démarrage auto)
 * @param {string} props.name - Nom de la caméra
 * @param {boolean} props.autoStart - Démarrer automatiquement le stream
 * @param {number} props.fps - Limite FPS (défaut: 15)
 * @param {number} props.quality - Qualité JPEG (défaut: 70)
 * @param {boolean} props.showOverlay - Afficher l'overlay avec les infos
 * @param {Function} props.onError - Callback en cas d'erreur
 */
const LiveStream = ({
  cameraId,
  rtspUrl = '',
  name = 'Camera',
  autoStart = true,
  fps = 15,
  quality = 70,
  showOverlay = true,
  onError = null
}) => {
  const [status, setStatus] = useState('idle'); // idle, loading, streaming, error
  const [error, setError] = useState(null);
  const [streamInfo, setStreamInfo] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const imgRef = useRef(null);
  const intervalRef = useRef(null);

  // Mettre à jour l'heure toutes les secondes
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const startStream = useCallback(async () => {
    setStatus('loading');
    setError(null);

    try {
      // Démarrer le stream côté serveur
      const response = await fetch(apiUrl('/streaming/start'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          camera_id: cameraId,
          rtsp_url: rtspUrl,
          name: name
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to start stream');
      }

      // Attendre un peu que le stream démarre
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Vérifier que le stream est actif
      const infoResponse = await fetch(apiUrl(`/streaming/info/${cameraId}`));
      if (infoResponse.ok) {
        const info = await infoResponse.json();
        setStreamInfo(info);
      }

      setStatus('streaming');
    } catch (err) {
      console.error('Stream error:', err);
      setError(err.message);
      setStatus('error');
      onError?.(err);
    }
  }, [cameraId, rtspUrl, name, onError]);

  // Démarrage automatique
  useEffect(() => {
    if (autoStart && cameraId && rtspUrl) {
      startStream();
    }
    
    return () => {
      // Cleanup si nécessaire
    };
  }, [autoStart, cameraId, rtspUrl, startStream]);

  const _stopStream = async () => {
    try {
      await fetch(apiUrl(`/streaming/stop/${cameraId}`), { method: 'POST' });
    } catch (err) {
      console.error('Stop stream error:', err);
    }
    setStatus('idle');
  };

  const handleImageError = () => {
    // L'image MJPEG a eu une erreur
    if (status === 'streaming') {
      setStatus('error');
      setError('Stream disconnected');
    }
  };

  const handleImageLoad = () => {
    // L'image charge correctement
    if (status === 'loading') {
      setStatus('streaming');
    }
  };

  // URL du stream MJPEG
  const streamUrl = apiUrl(`/streaming/mjpeg/${cameraId}?fps=${fps}&quality=${quality}&t=${Date.now()}`);

  return (
    <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
      
      {/* Stream vidéo */}
      {status === 'streaming' && (
        <img
          ref={imgRef}
          src={streamUrl}
          alt={`Live feed - ${name}`}
          className="w-full h-full object-contain"
          onError={handleImageError}
          onLoad={handleImageLoad}
        />
      )}

      {/* État: Chargement */}
      {status === 'loading' && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <div className="text-center">
            <Loader className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="text-gray-400">Connexion au flux...</p>
          </div>
        </div>
      )}

      {/* État: Idle (pas de stream) */}
      {status === 'idle' && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
          <div className="text-center">
            <Camera className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">Flux vidéo inactif</p>
            <button
              onClick={startStream}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 mx-auto"
            >
              <RefreshCw size={16} />
              Démarrer le flux
            </button>
          </div>
        </div>
      )}

      {/* État: Erreur */}
      {status === 'error' && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
          <div className="text-center">
            <WifiOff className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <p className="text-gray-400 mb-2">Connexion perdue</p>
            <p className="text-red-400 text-sm mb-4">{error}</p>
            <button
              onClick={startStream}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 mx-auto"
            >
              <RefreshCw size={16} />
              Reconnecter
            </button>
          </div>
        </div>
      )}

      {/* Overlay avec informations */}
      {showOverlay && status === 'streaming' && (
        <>
          {/* Badge LIVE */}
          <div className="absolute top-3 left-3 flex items-center gap-2">
            <span className="bg-red-600 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
              LIVE
            </span>
            <span className="bg-black/60 text-white text-xs px-2 py-1 rounded">
              {currentTime.toLocaleTimeString()}
            </span>
          </div>

          {/* Nom caméra */}
          <div className="absolute bottom-3 left-3">
            <span className="bg-black/60 text-white text-sm px-3 py-1 rounded">
              {name}
            </span>
          </div>

          {/* Infos stream */}
          {streamInfo && (
            <div className="absolute top-3 right-3 bg-black/60 text-white text-xs px-2 py-1 rounded">
              {streamInfo.width}x{streamInfo.height} @ {Math.round(streamInfo.fps)}fps
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default LiveStream;

/**
 * Composant de grille multi-caméras
 */
export const MultiCameraGrid = ({ cameras, columns = 2, fps = 10, quality = 60 }) => {
  return (
    <div className={`grid grid-cols-${columns} gap-2`}>
      {cameras.map((camera) => (
        <div key={camera.id} className="aspect-video">
          <LiveStream
            cameraId={camera.id}
            rtspUrl={camera.rtsp_url}
            name={camera.name}
            fps={fps}
            quality={quality}
            showOverlay={true}
          />
        </div>
      ))}
    </div>
  );
};

/**
 * Composant de snapshot (image unique)
 */
export const CameraSnapshot = ({ cameraId, refreshInterval = 5000, className = '' }) => {
  const [timestamp, setTimestamp] = useState(Date.now());
  
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(() => {
        setTimestamp(Date.now());
      }, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  return (
    <img
      src={apiUrl(`/streaming/snapshot/${cameraId}?quality=80&t=${timestamp}`)}
      alt="Camera snapshot"
      className={`object-contain ${className}`}
    />
  );
};
