import React from 'react';
import { useTranslation } from 'react-i18next';

const LANGS = [
  { code: 'fr', labelKey: 'common.languages.fr' },
  { code: 'en', labelKey: 'common.languages.en' },
  { code: 'es', labelKey: 'common.languages.es' }
];

export default function LanguageSwitcher({ className = '' }) {
  const { i18n, t } = useTranslation();

  const current = i18n.resolvedLanguage || i18n.language || 'fr';

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <span className="text-xs text-gray-400 hidden sm:inline">{t('common.language')}:</span>
      <div className="inline-flex rounded-full border border-white/10 bg-white/5 p-1">
        {LANGS.map(({ code, labelKey }) => {
          const active = current?.startsWith(code);
          return (
            <button
              key={code}
              type="button"
              onClick={() => i18n.changeLanguage(code)}
              className={`px-3 py-1 text-xs font-semibold rounded-full transition-colors ${
                active ? 'bg-ohm-cyan text-dark-950' : 'text-gray-300 hover:text-white'
              }`}
              aria-pressed={active}
              aria-label={t(labelKey)}
            >
              {code.toUpperCase()}
            </button>
          );
        })}
      </div>
    </div>
  );
}
