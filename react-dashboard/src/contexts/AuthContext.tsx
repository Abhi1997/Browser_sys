import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, UserRole } from '@/lib/types';
import { 
  getQueryParams, 
  setDeviceId, 
  setStoredToken, 
  getStoredToken,
  getDeviceId,
  extractUserFromToken,
  isTokenExpired,
  clearAuth
} from '@/lib/auth';
import { verifyToken } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  logout: () => void;
  selectedAdminId: string | null;
  setSelectedAdminId: (id: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAdminId, setSelectedAdminId] = useState<string | null>(null);

  const initializeAuth = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // First check URL params (from PyQt6)
      const params = getQueryParams();
      
      if (params.token && params.deviceId) {
        // Store from URL params
        setStoredToken(params.token);
        setDeviceId(params.deviceId);
      }

      const token = getStoredToken();
      const deviceId = getDeviceId();

      if (!token || !deviceId) {
        setError('Missing authentication credentials');
        setIsLoading(false);
        return;
      }

      if (isTokenExpired(token)) {
        setError('Session expired');
        clearAuth();
        setIsLoading(false);
        return;
      }

      // Extract user from token for immediate use
      const tokenUser = extractUserFromToken(token);
      if (tokenUser) {
        setUser(tokenUser);
      }

      // Verify with backend (in production)
      try {
        const response = await verifyToken();
        if (response.success && response.data) {
          setUser(response.data.user);
        }
      } catch {
        // If API fails, use token data (for demo/offline mode)
        console.log('Using token data (API verification unavailable)');
      }

    } catch (err) {
      setError('Authentication failed');
      console.error('Auth initialization error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
    setError(null);
  }, []);

  const value: AuthContextType = {
    user,
    role: user?.role || null,
    isLoading,
    isAuthenticated: !!user,
    error,
    logout,
    selectedAdminId,
    setSelectedAdminId,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
