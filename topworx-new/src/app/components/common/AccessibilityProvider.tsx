import React, { createContext, useContext, useState, useEffect } from 'react';

interface AccessibilityContextType {
  highContrast: boolean;
  toggleHighContrast: () => void;
  fontSize: 'small' | 'medium' | 'large';
  setFontSize: (size: 'small' | 'medium' | 'large') => void;
  reducedMotion: boolean;
  toggleReducedMotion: () => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [highContrast, setHighContrast] = useState(false);
  const [fontSize, setFontSizeState] = useState<'small' | 'medium' | 'large'>('medium');
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    // Load accessibility settings from localStorage
    const savedHighContrast = localStorage.getItem('highContrast') === 'true';
    const savedFontSize = localStorage.getItem('fontSize') as 'small' | 'medium' | 'large' || 'medium';
    const savedReducedMotion = localStorage.getItem('reducedMotion') === 'true';

    setHighContrast(savedHighContrast);
    setFontSizeState(savedFontSize);
    setReducedMotion(savedReducedMotion);
  }, []);

  useEffect(() => {
    // Apply accessibility settings to document
    document.documentElement.setAttribute('data-high-contrast', highContrast.toString());
    document.documentElement.setAttribute('data-font-size', fontSize);
    document.documentElement.setAttribute('data-reduced-motion', reducedMotion.toString());
    
    // Save to localStorage
    localStorage.setItem('highContrast', highContrast.toString());
    localStorage.setItem('fontSize', fontSize);
    localStorage.setItem('reducedMotion', reducedMotion.toString());
  }, [highContrast, fontSize, reducedMotion]);

  const toggleHighContrast = () => {
    setHighContrast(prev => !prev);
  };

  const setFontSize = (size: 'small' | 'medium' | 'large') => {
    setFontSizeState(size);
  };

  const toggleReducedMotion = () => {
    setReducedMotion(prev => !prev);
  };

  return (
    <AccessibilityContext.Provider value={{
      highContrast,
      toggleHighContrast,
      fontSize,
      setFontSize,
      reducedMotion,
      toggleReducedMotion
    }}>
      {children}
    </AccessibilityContext.Provider>
  );
}; 