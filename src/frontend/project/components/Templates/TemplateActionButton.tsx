import React from 'react';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface TemplateActionButtonProps {
  onClick: () => void;
  isLoading: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  children: React.ReactNode;
  disabled?: boolean;
}

export const TemplateActionButton: React.FC<TemplateActionButtonProps> = ({
  onClick,
  isLoading,
  variant = 'primary',
  children,
  disabled = false
}) => {
  const baseClasses = 'px-4 py-2 rounded-md font-medium transition-colors duration-200 flex items-center gap-2';
  const variantClasses = {
    primary: 'bg-primary text-white hover:bg-primary-dark disabled:bg-gray-400',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-100',
    danger: 'bg-red-500 text-white hover:bg-red-600 disabled:bg-red-300'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`${baseClasses} ${variantClasses[variant]}`}
    >
      {isLoading && <LoadingSpinner size="sm" />}
      {children}
    </button>
  );
};