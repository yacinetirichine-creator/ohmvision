/**
 * OhmVision - Setup Wizard
 * Assistant de configuration première installation
 */

import React, { useState, useEffect } from 'react';

// ============================================================================
// Composant Principal
// ============================================================================

export default function SetupWizard({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Données du wizard
  const [adminData, setAdminData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    companyName: ''
  });
  
  const [discoveredDevices, setDiscoveredDevices] = useState([]);
  const [selectedCameras, setSelectedCameras] = useState([]);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanStatus, setScanStatus] = useState('idle');
  
  const [manualCamera, setManualCamera] = useState({
    name: '',
    ip: '',
    rtspUrl: '',
    username: 'admin',
    password: ''
  });

  // Vérifier l'état initial
  useEffect(() => {
    checkSetupStatus();
  }, []);

  const checkSetupStatus = async () => {
    try {
      const response = await fetch('/api/setup/status');
      const data = await response.json();
      
      if (data.setup_completed) {
        onComplete?.();
        return;
      }
      
      setCurrentStep(data.current_step);
      setLoading(false);
    } catch (err) {
      console.error('Error checking setup status:', err);
      setLoading(false);
    }
  };

  // Steps du wizard
  const steps = [
    { id: 'welcome', title: 'Bienvenue', icon: '🎥' },
    { id: 'admin', title: 'Administrateur', icon: '👤' },
    { id: 'cameras', title: 'Caméras', icon: '📹' },
    { id: 'detections', title: 'Détections', icon: '🤖' },
    { id: 'complete', title: 'Terminé', icon: '✅' }
  ];

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🎥 OhmVision
          </h1>
          <p className="text-blue-200">
            Configurez votre système de vidéosurveillance intelligente
          </p>
        </div>

        {/* Progress Steps */}
        <StepIndicator steps={steps} currentStep={currentStep} />

        {/* Content Card */}
        <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">
          
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 m-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Step Content */}
          <div className="p-8">
            {currentStep === 0 && (
              <WelcomeStep onNext={() => setCurrentStep(1)} />
            )}
            
            {currentStep === 1 && (
              <AdminStep 
                data={adminData}
                onChange={setAdminData}
                onNext={handleAdminSubmit}
                onBack={() => setCurrentStep(0)}
                error={error}
                setError={setError}
              />
            )}
            
            {currentStep === 2 && (
              <CamerasStep
                discoveredDevices={discoveredDevices}
                setDiscoveredDevices={setDiscoveredDevices}
                selectedCameras={selectedCameras}
                setSelectedCameras={setSelectedCameras}
                scanProgress={scanProgress}
                setScanProgress={setScanProgress}
                scanStatus={scanStatus}
                setScanStatus={setScanStatus}
                manualCamera={manualCamera}
                setManualCamera={setManualCamera}
                onNext={handleCamerasSubmit}
                onBack={() => setCurrentStep(1)}
                setError={setError}
              />
            )}
            
            {currentStep === 3 && (
              <DetectionsStep
                cameras={selectedCameras}
                setCameras={setSelectedCameras}
                onNext={handleDetectionsSubmit}
                onBack={() => setCurrentStep(2)}
              />
            )}
            
            {currentStep === 4 && (
              <CompleteStep onFinish={handleFinish} />
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // Handlers
  async function handleAdminSubmit() {
    setError(null);
    
    if (adminData.password !== adminData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }
    
    if (adminData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }
    
    try {
      const response = await fetch('/api/setup/admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: adminData.email,
          password: adminData.password,
          full_name: adminData.fullName,
          company_name: adminData.companyName
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Erreur lors de la création du compte');
      }
      
      setCurrentStep(2);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCamerasSubmit() {
    if (selectedCameras.length === 0) {
      setError('Veuillez ajouter au moins une caméra');
      return;
    }
    
    try {
      const camerasToAdd = selectedCameras.map(cam => ({
        name: cam.name || `Camera ${cam.ip}`,
        ip: cam.ip,
        rtsp_url: cam.rtsp_url || cam.rtspUrl,
        username: cam.username || '',
        password: cam.password || '',
        manufacturer: cam.manufacturer,
        model: cam.model,
        enabled_detections: ['person']  // Par défaut
      }));
      
      const response = await fetch('/api/setup/cameras', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(camerasToAdd)
      });
      
      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout des caméras');
      }
      
      setCurrentStep(3);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDetectionsSubmit() {
    setCurrentStep(4);
  }

  async function handleFinish() {
    try {
      const response = await fetch('/api/setup/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          enable_notifications: true,
          notification_email: adminData.email
        })
      });
      
      const data = await response.json();
      
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
      }
      
      onComplete?.();
    } catch (err) {
      setError(err.message);
    }
  }
}

// ============================================================================
// Sous-composants
// ============================================================================

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-white border-t-transparent mx-auto mb-4"></div>
        <p className="text-white text-xl">Chargement...</p>
      </div>
    </div>
  );
}

function StepIndicator({ steps, currentStep }) {
  return (
    <div className="flex justify-center mb-8">
      <div className="flex items-center space-x-2">
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div className={`
              flex items-center justify-center w-10 h-10 rounded-full text-lg
              ${index <= currentStep 
                ? 'bg-white text-purple-900' 
                : 'bg-white/20 text-white/60'}
              transition-all duration-300
            `}>
              {index < currentStep ? '✓' : step.icon}
            </div>
            {index < steps.length - 1 && (
              <div className={`
                w-12 h-1 rounded
                ${index < currentStep ? 'bg-white' : 'bg-white/20'}
              `}></div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function WelcomeStep({ onNext }) {
  return (
    <div className="text-center py-8">
      <div className="text-6xl mb-6">🎥</div>
      <h2 className="text-3xl font-bold text-gray-800 mb-4">
        Bienvenue dans OhmVision
      </h2>
      <p className="text-gray-600 mb-8 max-w-md mx-auto">
        Configurons votre système de vidéosurveillance intelligente 
        en quelques étapes simples.
      </p>
      
      <div className="grid grid-cols-2 gap-4 max-w-md mx-auto mb-8 text-left">
        <div className="flex items-center p-3 bg-blue-50 rounded-lg">
          <span className="text-2xl mr-3">👤</span>
          <span className="text-sm text-gray-700">Créer un compte admin</span>
        </div>
        <div className="flex items-center p-3 bg-green-50 rounded-lg">
          <span className="text-2xl mr-3">📹</span>
          <span className="text-sm text-gray-700">Scanner vos caméras</span>
        </div>
        <div className="flex items-center p-3 bg-purple-50 rounded-lg">
          <span className="text-2xl mr-3">🤖</span>
          <span className="text-sm text-gray-700">Configurer l'IA</span>
        </div>
        <div className="flex items-center p-3 bg-orange-50 rounded-lg">
          <span className="text-2xl mr-3">✅</span>
          <span className="text-sm text-gray-700">C'est prêt !</span>
        </div>
      </div>
      
      <button
        onClick={onNext}
        className="px-8 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors"
      >
        Commencer →
      </button>
    </div>
  );
}

function AdminStep({ data, onChange, onNext, onBack, error, setError }) {
  const handleChange = (field, value) => {
    onChange({ ...data, [field]: value });
    setError(null);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        👤 Créer le compte administrateur
      </h2>
      <p className="text-gray-600 mb-6">
        Ce compte vous permettra de gérer OhmVision.
      </p>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nom complet
          </label>
          <input
            type="text"
            value={data.fullName}
            onChange={(e) => handleChange('fullName', e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Jean Dupont"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={data.email}
            onChange={(e) => handleChange('email', e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="admin@example.com"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Mot de passe
          </label>
          <input
            type="password"
            value={data.password}
            onChange={(e) => handleChange('password', e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="••••••••"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Confirmer le mot de passe
          </label>
          <input
            type="password"
            value={data.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="••••••••"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nom de l'entreprise (optionnel)
          </label>
          <input
            type="text"
            value={data.companyName}
            onChange={(e) => handleChange('companyName', e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Ma Société"
          />
        </div>
      </div>
      
      <div className="flex justify-between mt-8">
        <button
          onClick={onBack}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          ← Retour
        </button>
        <button
          onClick={onNext}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700"
        >
          Continuer →
        </button>
      </div>
    </div>
  );
}

function CamerasStep({
  discoveredDevices, setDiscoveredDevices,
  selectedCameras, setSelectedCameras,
  scanProgress, setScanProgress,
  scanStatus, setScanStatus,
  manualCamera, setManualCamera,
  onNext, onBack, setError
}) {
  const [showManualForm, setShowManualForm] = useState(false);
  const [testingCamera, setTestingCamera] = useState(null);

  const startScan = async () => {
    setScanStatus('scanning');
    setScanProgress(0);
    setDiscoveredDevices([]);
    
    try {
      // Démarrer le scan
      await fetch('/api/discovery/scan/start', { method: 'POST' });
      
      // Polling du status
      const pollStatus = async () => {
        const response = await fetch('/api/discovery/scan/status');
        const data = await response.json();
        
        setScanProgress(data.progress);
        
        if (data.devices) {
          setDiscoveredDevices(data.devices.filter(d => 
            d.device_type === 'camera' || d.open_ports?.includes(554)
          ));
        }
        
        if (data.status === 'completed') {
          setScanStatus('completed');
          return;
        }
        
        if (data.status === 'scanning') {
          setTimeout(pollStatus, 1000);
        }
      };
      
      pollStatus();
    } catch (err) {
      setScanStatus('error');
      setError('Erreur lors du scan réseau');
    }
  };

  const testCamera = async (device) => {
    setTestingCamera(device.ip);
    
    try {
      const response = await fetch('/api/discovery/rtsp/auto-discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ip: device.ip,
          username: device.username || 'admin',
          password: device.password || '',
          manufacturer: device.manufacturer
        })
      });
      
      const data = await response.json();
      
      if (data.is_valid) {
        // Mettre à jour l'appareil avec l'URL RTSP trouvée
        const updated = discoveredDevices.map(d => 
          d.ip === device.ip 
            ? { ...d, rtsp_url: data.url, rtsp_valid: true, resolution: `${data.width}x${data.height}` }
            : d
        );
        setDiscoveredDevices(updated);
      }
    } catch (err) {
      console.error('Test error:', err);
    }
    
    setTestingCamera(null);
  };

  const toggleCameraSelection = (device) => {
    const exists = selectedCameras.find(c => c.ip === device.ip);
    if (exists) {
      setSelectedCameras(selectedCameras.filter(c => c.ip !== device.ip));
    } else {
      setSelectedCameras([...selectedCameras, device]);
    }
  };

  const addManualCamera = async () => {
    if (!manualCamera.ip) {
      setError('Veuillez entrer une adresse IP');
      return;
    }
    
    // Tester la connexion
    setTestingCamera('manual');
    
    try {
      let rtspUrl = manualCamera.rtspUrl;
      
      if (!rtspUrl) {
        // Auto-découverte
        const response = await fetch('/api/discovery/rtsp/auto-discover', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ip: manualCamera.ip,
            username: manualCamera.username,
            password: manualCamera.password
          })
        });
        
        const data = await response.json();
        if (data.is_valid) {
          rtspUrl = data.url;
        }
      }
      
      const newCamera = {
        ip: manualCamera.ip,
        name: manualCamera.name || `Camera ${manualCamera.ip}`,
        rtsp_url: rtspUrl,
        username: manualCamera.username,
        password: manualCamera.password,
        device_type: 'camera',
        rtsp_valid: !!rtspUrl
      };
      
      setSelectedCameras([...selectedCameras, newCamera]);
      setShowManualForm(false);
      setManualCamera({ name: '', ip: '', rtspUrl: '', username: 'admin', password: '' });
      
    } catch (err) {
      setError('Erreur lors du test de la caméra');
    }
    
    setTestingCamera(null);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        📹 Rechercher vos caméras
      </h2>
      <p className="text-gray-600 mb-6">
        OhmVision peut scanner votre réseau pour trouver automatiquement vos caméras.
      </p>
      
      {/* Scan Button */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={startScan}
          disabled={scanStatus === 'scanning'}
          className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {scanStatus === 'scanning' ? (
            <>
              <span className="animate-spin">🔄</span>
              Scan en cours... {scanProgress}%
            </>
          ) : (
            <>
              🔍 Scanner le réseau
            </>
          )}
        </button>
        
        <button
          onClick={() => setShowManualForm(!showManualForm)}
          className="px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          ➕ Ajouter manuellement
        </button>
      </div>
      
      {/* Progress Bar */}
      {scanStatus === 'scanning' && (
        <div className="mb-6">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${scanProgress}%` }}
            ></div>
          </div>
        </div>
      )}
      
      {/* Manual Form */}
      {showManualForm && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="font-semibold mb-3">Ajouter une caméra manuellement</h3>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Nom (ex: Entrée)"
              value={manualCamera.name}
              onChange={(e) => setManualCamera({...manualCamera, name: e.target.value})}
              className="px-3 py-2 border rounded-lg"
            />
            <input
              type="text"
              placeholder="Adresse IP"
              value={manualCamera.ip}
              onChange={(e) => setManualCamera({...manualCamera, ip: e.target.value})}
              className="px-3 py-2 border rounded-lg"
            />
            <input
              type="text"
              placeholder="Utilisateur (admin)"
              value={manualCamera.username}
              onChange={(e) => setManualCamera({...manualCamera, username: e.target.value})}
              className="px-3 py-2 border rounded-lg"
            />
            <input
              type="password"
              placeholder="Mot de passe"
              value={manualCamera.password}
              onChange={(e) => setManualCamera({...manualCamera, password: e.target.value})}
              className="px-3 py-2 border rounded-lg"
            />
            <input
              type="text"
              placeholder="URL RTSP (optionnel, auto-détectée)"
              value={manualCamera.rtspUrl}
              onChange={(e) => setManualCamera({...manualCamera, rtspUrl: e.target.value})}
              className="col-span-2 px-3 py-2 border rounded-lg"
            />
          </div>
          <button
            onClick={addManualCamera}
            disabled={testingCamera === 'manual'}
            className="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {testingCamera === 'manual' ? 'Test en cours...' : 'Ajouter'}
          </button>
        </div>
      )}
      
      {/* Discovered Devices */}
      {discoveredDevices.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3">
            Appareils détectés ({discoveredDevices.length})
          </h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {discoveredDevices.map((device) => (
              <div 
                key={device.ip}
                className={`
                  flex items-center justify-between p-3 rounded-lg border-2 cursor-pointer
                  ${selectedCameras.find(c => c.ip === device.ip)
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'}
                `}
                onClick={() => toggleCameraSelection(device)}
              >
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={!!selectedCameras.find(c => c.ip === device.ip)}
                    onChange={() => {}}
                    className="w-5 h-5 text-purple-600"
                  />
                  <div>
                    <div className="font-medium">
                      {device.ip}
                      {device.manufacturer && (
                        <span className="ml-2 text-sm text-gray-500">
                          ({device.manufacturer})
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {device.is_onvif && <span className="mr-2">📷 ONVIF</span>}
                      {device.rtsp_valid && <span className="text-green-600">✓ RTSP OK</span>}
                      {device.resolution && <span className="ml-2">{device.resolution}</span>}
                    </div>
                  </div>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); testCamera(device); }}
                  disabled={testingCamera === device.ip}
                  className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                >
                  {testingCamera === device.ip ? '...' : 'Tester'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Selected Cameras Summary */}
      {selectedCameras.length > 0 && (
        <div className="bg-green-50 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-green-800 mb-2">
            ✓ {selectedCameras.length} caméra(s) sélectionnée(s)
          </h3>
          <div className="text-sm text-green-700">
            {selectedCameras.map(c => c.ip).join(', ')}
          </div>
        </div>
      )}
      
      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <button
          onClick={onBack}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          ← Retour
        </button>
        <button
          onClick={onNext}
          disabled={selectedCameras.length === 0}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continuer →
        </button>
      </div>
    </div>
  );
}

function DetectionsStep({ cameras, setCameras, onNext, onBack }) {
  const detectionTypes = [
    { id: 'person', label: 'Détection de personnes', icon: '👤', description: 'Détecte les personnes dans le champ de vision' },
    { id: 'fall', label: 'Détection de chute', icon: '⚠️', description: 'Alerte en cas de chute d\'une personne' },
    { id: 'fire', label: 'Détection feu/fumée', icon: '🔥', description: 'Détecte les départs de feu et la fumée' },
    { id: 'ppe', label: 'Détection EPI', icon: '🦺', description: 'Vérifie le port du casque et du gilet' },
    { id: 'counting', label: 'Comptage', icon: '📊', description: 'Compte les entrées et sorties' }
  ];

  const toggleDetection = (cameraIndex, detectionId) => {
    const updated = [...cameras];
    if (!updated[cameraIndex].enabled_detections) {
      updated[cameraIndex].enabled_detections = ['person'];
    }
    
    const detections = updated[cameraIndex].enabled_detections;
    const index = detections.indexOf(detectionId);
    
    if (index >= 0) {
      detections.splice(index, 1);
    } else {
      detections.push(detectionId);
    }
    
    setCameras(updated);
  };

  const enableAllDetections = (detectionId) => {
    const updated = cameras.map(cam => {
      if (!cam.enabled_detections) cam.enabled_detections = [];
      if (!cam.enabled_detections.includes(detectionId)) {
        cam.enabled_detections.push(detectionId);
      }
      return cam;
    });
    setCameras(updated);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        🤖 Configurer les détections IA
      </h2>
      <p className="text-gray-600 mb-6">
        Choisissez les analyses à activer pour chaque caméra.
      </p>
      
      {/* Quick Enable All */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold mb-3">Activer pour toutes les caméras :</h3>
        <div className="flex flex-wrap gap-2">
          {detectionTypes.map(det => (
            <button
              key={det.id}
              onClick={() => enableAllDetections(det.id)}
              className="px-3 py-1 bg-white border rounded-full text-sm hover:bg-purple-50 hover:border-purple-300"
            >
              {det.icon} {det.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Per Camera Config */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {cameras.map((camera, cameraIndex) => (
          <div key={camera.ip} className="border rounded-lg p-4">
            <h3 className="font-semibold mb-3">
              📹 {camera.name || camera.ip}
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {detectionTypes.map(det => {
                const enabled = camera.enabled_detections?.includes(det.id);
                return (
                  <label
                    key={det.id}
                    className={`
                      flex items-center gap-2 p-2 rounded-lg cursor-pointer
                      ${enabled ? 'bg-purple-100 border-purple-300' : 'bg-gray-50'}
                      border hover:border-purple-300
                    `}
                  >
                    <input
                      type="checkbox"
                      checked={enabled}
                      onChange={() => toggleDetection(cameraIndex, det.id)}
                      className="w-4 h-4 text-purple-600"
                    />
                    <span className="text-lg">{det.icon}</span>
                    <span className="text-sm">{det.label}</span>
                  </label>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <button
          onClick={onBack}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          ← Retour
        </button>
        <button
          onClick={onNext}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700"
        >
          Continuer →
        </button>
      </div>
    </div>
  );
}

function CompleteStep({ onFinish }) {
  const [finishing, setFinishing] = useState(false);

  const handleFinish = async () => {
    setFinishing(true);
    await onFinish();
  };

  return (
    <div className="text-center py-8">
      <div className="text-6xl mb-6">🎉</div>
      <h2 className="text-3xl font-bold text-gray-800 mb-4">
        Configuration terminée !
      </h2>
      <p className="text-gray-600 mb-8 max-w-md mx-auto">
        Votre système OhmVision est prêt. Vos caméras sont configurées 
        et l'analyse IA est activée.
      </p>
      
      <div className="bg-green-50 rounded-lg p-6 max-w-md mx-auto mb-8">
        <h3 className="font-semibold text-green-800 mb-4">Ce qui vous attend :</h3>
        <ul className="text-left text-green-700 space-y-2">
          <li>✓ Dashboard en temps réel</li>
          <li>✓ Alertes instantanées</li>
          <li>✓ Analyses IA 24/7</li>
          <li>✓ Historique des événements</li>
        </ul>
      </div>
      
      <button
        onClick={handleFinish}
        disabled={finishing}
        className="px-8 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50"
      >
        {finishing ? 'Finalisation...' : 'Ouvrir le Dashboard →'}
      </button>
    </div>
  );
}
