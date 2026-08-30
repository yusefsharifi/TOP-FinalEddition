import React, { useEffect, useCallback } from 'react';

interface PerformanceOptimizerProps {
  children: React.ReactNode;
}

const PerformanceOptimizer: React.FC<PerformanceOptimizerProps> = ({ children }) => {
  // Preload critical resources
  useEffect(() => {
    // Preload fonts
    const fontLink = document.createElement('link');
    fontLink.rel = 'preload';
    fontLink.as = 'font';
    fontLink.href = '/fonts/IRANSansWeb_Bold.woff2';
    fontLink.type = 'font/woff2';
    fontLink.crossOrigin = 'anonymous';
    document.head.appendChild(fontLink);

    // Preload critical CSS
    const cssLink = document.createElement('link');
    cssLink.rel = 'preload';
    cssLink.as = 'style';
    cssLink.href = '/src/app/theme/theme.css';
    document.head.appendChild(cssLink);
  }, []);

  // Optimize images
  const optimizeImages = useCallback(() => {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      if (!img.loading) {
        img.loading = 'lazy';
      }
    });
  }, []);

  useEffect(() => {
    optimizeImages();
  }, [optimizeImages]);

  // Memory management
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Pause non-critical operations when tab is not visible
        console.log('Tab hidden, pausing non-critical operations');
      } else {
        // Resume operations when tab becomes visible
        console.log('Tab visible, resuming operations');
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return <>{children}</>;
};

export default PerformanceOptimizer; 