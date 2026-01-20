import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import fr from './locales/fr.json';
import en from './locales/en.json';
import es from './locales/es.json';

const resources = {
  fr: { translation: fr },
  en: { translation: en },
  es: { translation: es }
};

const STORAGE_KEY = 'ohmvision_language';
const hostname = typeof window !== 'undefined' ? String(window.location.hostname || '').toLowerCase() : '';
const defaultLang = hostname.endsWith('ohmvision.app') || hostname === 'ohmvision.app' ? 'en' : 'fr';

// Si l'utilisateur n'a pas encore choisi de langue, on force un défaut cohérent par domaine.
try {
  if (typeof window !== 'undefined' && !localStorage.getItem(STORAGE_KEY)) {
    localStorage.setItem(STORAGE_KEY, defaultLang);
  }
} catch {
  // ignore
}

if (!i18n.isInitialized) {
  i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
      resources,
      fallbackLng: defaultLang,
      supportedLngs: ['fr', 'en', 'es'],
      interpolation: { escapeValue: false },
      detection: {
        order: ['localStorage', 'navigator'],
        caches: ['localStorage'],
        lookupLocalStorage: STORAGE_KEY
      }
    });
}

export default i18n;
