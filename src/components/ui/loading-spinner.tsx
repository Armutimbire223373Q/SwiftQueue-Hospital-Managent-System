import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  text?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  className,
  text
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <Loader2 className={cn('animate-spin text-blue-600', sizeClasses[size])} />
      {text && <span className="ml-2 text-sm text-gray-600">{text}</span>}
    </div>
  );
};

interface LoadingOverlayProps {
  isVisible: boolean;
  text?: string;
  className?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isVisible,
  text = 'Loading...',
  className
}) => {
  if (!isVisible) return null;

  return (
    <div className={cn(
      'absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-50 rounded-lg',
      className
    )}>
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-2 text-sm text-gray-600">{text}</p>
      </div>
    </div>
  );
};

interface LoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  loadingText?: string;
  children: React.ReactNode;
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  loadingText = 'Loading...',
  children,
  disabled,
  className,
  ...props
}) => {
  return (
    <button
      {...props}
      disabled={loading || disabled}
      className={cn(
        'inline-flex items-center justify-center',
        className
      )}
    >
      {loading && <LoadingSpinner size="sm" className="mr-2" />}
      {loading ? loadingText : children}
    </button>
  );
};