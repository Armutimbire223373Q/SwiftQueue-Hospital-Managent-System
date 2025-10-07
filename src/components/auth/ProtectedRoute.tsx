import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
  requireAuth?: boolean;
}

export default function ProtectedRoute({
  children,
  requiredRole,
  requireAuth = true
}: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  const isGuestSession = localStorage.getItem('isGuestSession') === 'true';

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If authentication is required but user is not authenticated and not a guest
  if (requireAuth && !isAuthenticated && !isGuestSession) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If user is authenticated but trying to access auth pages (login/register)
  if (!requireAuth && (isAuthenticated || isGuestSession)) {
    // Redirect based on role or guest status
    if (isGuestSession) {
      return <Navigate to="/" replace />;
    }
    switch (user?.role) {
      case 'admin':
        return <Navigate to="/admin" replace />;
      case 'staff':
        return <Navigate to="/dashboard" replace />;
      default:
        return <Navigate to="/" replace />;
    }
  }

  // Check role-based access (guests can't access admin/staff areas)
  if (requiredRole && !isGuestSession && user?.role !== requiredRole && user?.role !== 'admin') {
    // Redirect to appropriate dashboard based on user role
    switch (user?.role) {
      case 'staff':
        return <Navigate to="/dashboard" replace />;
      default:
        return <Navigate to="/" replace />;
    }
  }

  // Block guest access to admin/staff areas
  if (isGuestSession && (requiredRole === 'admin' || requiredRole === 'staff')) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}