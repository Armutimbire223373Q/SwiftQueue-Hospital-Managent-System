import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, authService } from '@/services/authService';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  updateProfile: (updates: { name?: string; phone?: string }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const initializeAuth = async () => {
      const token = authService.getToken();
      const storedUser = authService.getCurrentUserFromStorage();
      const isGuestSession = localStorage.getItem('isGuestSession') === 'true';

      if (isGuestSession && storedUser) {
        // Handle guest session
        setUser(storedUser);
      } else if (token && storedUser) {
        try {
          // Check if token is expired or expiring soon
          if (authService.isTokenExpired()) {
            // Try to refresh token
            try {
              await authService.refreshToken();
              const currentUser = await authService.getCurrentUser();
              setUser(currentUser);
            } catch (refreshError) {
              // Refresh failed, logout
              authService.logout();
            }
          } else {
            // Token is valid, verify with server
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
          }
        } catch (error) {
          // Token verification failed, try refresh
          try {
            await authService.refreshToken();
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
          } catch (refreshError) {
            // Both verification and refresh failed, logout
            authService.logout();
          }
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password);

    if (response.access_token) {
      // Store token
      localStorage.setItem('token', response.access_token);

      // Get and store user profile
      const userProfile = await authService.getCurrentUser();
      localStorage.setItem('user', JSON.stringify(userProfile));
      setUser(userProfile);
    }
  };

  const register = async (userData: any) => {
    await authService.register(userData);
  };

  const logout = () => {
    authService.logout();
    localStorage.removeItem('isGuestSession');
    setUser(null);
  };

  const updateProfile = async (updates: { name?: string; phone?: string }) => {
    await authService.updateProfile(updates);
    if (user) {
      const updatedUser = { ...user, ...updates };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};