import React from 'react';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface TemplateActionButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  children: React.ReactNode;
  className?: string;
}

export const TemplateActionButton: React.FC<TemplateActionButtonProps> = ({
  onClick,
  isLoading = false,
  variant = 'primary',
  children,
  className,
}) => {
  const baseStyles = 'px-3 py-1.5 text-sm font-medium rounded-md flex items-center';
  
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600',
    danger: 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/20 dark:text-red-500 dark:hover:bg-red-900/30'
  };

  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={`${baseStyles} ${variantStyles[variant]} ${className || ''} ${
        isLoading ? 'opacity-75 cursor-not-allowed' : ''
      }`}
    >
      {isLoading && <LoadingSpinner size="sm" className="mr-2" />}
      {children}
    </button>
  );
};