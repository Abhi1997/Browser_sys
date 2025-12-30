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
      if (!tokenUser) {
        setError('Failed to extract user information from token. Token may be invalid or malformed.');
        setIsLoading(false);
        return;
      }
      
      // Set user immediately from token
      setUser(tokenUser);

      // Verify with backend (in production)
      try {
        const response = await verifyToken();
        if (response.success && response.data) {
          // Update user with verified data from backend
          setUser(response.data.user);
        } else {
          // API verification failed, but we have token data, so continue with token user
          // Don't set error here - we'll use token data as fallback
        }
      } catch (err) {
        // If API fails, use token data (for demo/offline mode)
        // Don't set error here - we'll use token data as fallback
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

  // Show error in UI if authentication fails (for PyQt6 browsers without console)
  if (error && !isLoading) {
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center', 
        fontFamily: 'system-ui, -apple-system, sans-serif',
        background: '#fef2f2',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <h1 style={{ color: '#dc2626', fontSize: '1.5rem', marginBottom: '1rem' }}>
          Authentication Error
        </h1>
        <p style={{ color: '#991b1b', fontSize: '1rem', marginBottom: '0.5rem' }}>
          {error}
        </p>
        <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '1rem' }}>
          Please close this window and try opening the dashboard again from the browser application.
        </p>
        <div style={{ marginTop: '2rem', padding: '1rem', background: '#fff', borderRadius: '0.5rem', textAlign: 'left', maxWidth: '600px' }}>
          <p style={{ fontSize: '0.875rem', color: '#374151', marginBottom: '0.5rem' }}>
            <strong>Debug Information:</strong>
          </p>
          <p style={{ fontSize: '0.75rem', color: '#6b7280', fontFamily: 'monospace' }}>
            User: {user ? user.username : 'Not loaded'}<br/>
            Role: {user?.role || 'Not set'} (Type: {typeof user?.role})<br/>
            Loading: {isLoading ? 'Yes' : 'No'}<br/>
            Authenticated: {!!user ? 'Yes' : 'No'}<br/>
            Error: {error || 'None'}
          </p>
        </div>
      </div>
    );
  }
  
  // Show debug info if user is not authenticated (even without error)
  if (!isLoading && !user && !error) {
    // Try to get token from URL to debug
    const params = getQueryParams();
    const hasToken = !!params.token;
    const hasDeviceId = !!params.deviceId;
    
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center', 
        fontFamily: 'system-ui, -apple-system, sans-serif',
        background: '#fef9e7',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <h1 style={{ color: '#d97706', fontSize: '1.5rem', marginBottom: '1rem' }}>
          Authentication Failed
        </h1>
        <p style={{ color: '#92400e', fontSize: '1rem', marginBottom: '0.5rem' }}>
          Could not extract user information from token.
        </p>
        <div style={{ marginTop: '2rem', padding: '1rem', background: '#fff', borderRadius: '0.5rem', textAlign: 'left', maxWidth: '600px' }}>
          <p style={{ fontSize: '0.875rem', color: '#374151', marginBottom: '0.5rem' }}>
            <strong>Debug Information:</strong>
          </p>
          <p style={{ fontSize: '0.75rem', color: '#6b7280', fontFamily: 'monospace' }}>
            Token in URL: {hasToken ? 'Yes' : 'No'}<br/>
            Device ID in URL: {hasDeviceId ? 'Yes' : 'No'}<br/>
            Loading: {isLoading ? 'Yes' : 'No'}<br/>
            User: {user ? user.username : 'Not loaded'}<br/>
            Role: {user?.role || 'Not set'}
          </p>
        </div>
        <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '1rem' }}>
          Please close this window and try opening the dashboard again from the browser application.
        </p>
      </div>
    );
  }

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
