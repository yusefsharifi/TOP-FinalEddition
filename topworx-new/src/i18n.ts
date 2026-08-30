import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import fa from './i18n/locales/fa';
import en from './i18n/locales/en';

i18n.use(initReactI18next).init({
  resources: {
    fa: {
      translation: fa,
    },
    en: {
      translation: en,
    },
  },
  lng: 'fa',
  fallbackLng: 'fa',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n; 