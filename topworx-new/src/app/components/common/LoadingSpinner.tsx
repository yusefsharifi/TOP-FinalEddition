import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  text?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  color = 'var(--primary-color)',
  text 
}) => {
  const sizeMap = {
    small: '16px',
    medium: '24px',
    large: '32px'
  };

  return (
    <div className="loading-container">
      <div 
        className="loading-spinner"
        style={{
          width: sizeMap[size],
          height: sizeMap[size],
          borderColor: color,
          borderTopColor: 'transparent'
        }}
      />
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
};

export { LoadingSpinner };
export default LoadingSpinner;