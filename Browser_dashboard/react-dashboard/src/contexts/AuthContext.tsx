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

/** Routes that do not require dashboard auth (anyone can access) */
const PUBLIC_AUTH_ROUTES = ['/forgot-password', '/reset-password'];

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  logout: () => void;
  refreshUser: () => Promise<void>;
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
      // First check URL params (from PyQt6 or direct access)
      const params = getQueryParams();
      
      if (params.token && params.deviceId) {
        // Store from URL params
        setStoredToken(params.token);
        setDeviceId(params.deviceId);
      }

      const token = getStoredToken();
      const deviceId = getDeviceId();

      if (!token || !deviceId) {
        setError('Missing authentication credentials. Please login to access the dashboard.');
        setIsLoading(false);
        return;
      }

      // Check token expiry first
      if (isTokenExpired(token)) {
        setError('Session expired. Please login again.');
        clearAuth();
        setIsLoading(false);
        return;
      }

      // Extract user from token for immediate use
      const tokenUser = extractUserFromToken(token);
      if (!tokenUser) {
        setError('Failed to extract user information from token. Token may be invalid or malformed.');
        clearAuth();
        setIsLoading(false);
        return;
      }
      
      // Set user immediately from token
      setUser(tokenUser);

      // Attempt backend verification to get real user data from database
      // If backend is not available, continue with token data (local dev mode)
      try {
        const response = await verifyToken();
        if (response.success && response.data) {
          // Update user with verified data from backend (real database data)
          const verifiedUser = response.data.user;
          setUser(verifiedUser);
        } else {
          // Backend verification failed - check if it's a connection error or auth error
          const errMsg = response.error ?? '';
          const isLocalhost = !import.meta.env.VITE_API_URL ||
                             import.meta.env.VITE_API_URL.includes('localhost') ||
                             import.meta.env.VITE_API_URL.includes('127.0.0.1');

          if (isLocalhost && (errMsg.includes('Cannot connect') || errMsg.includes('fetch'))) {
            // Backend not running - use token from URL (expected in local dev / PyQt)
            console.log('Backend not available; using token from URL for session.');
          } else if (errMsg.includes('Signature verification failed') ||
                     errMsg.includes('Invalid token') ||
                     errMsg.includes('expired token')) {
            // Backend exists but token is invalid - this is a real error
            setError('Token verification failed. Please check JWT_SECRET matches between browser app and backend.');
            clearAuth();
            setIsLoading(false);
            return;
          } else {
            // Other backend errors (or no error message) - continue with token from URL
            console.warn('Backend verification failed; using token from URL for session.', errMsg || '(no message)');
          }
        }
      } catch (err) {
        // Network error - continue with token from URL (backend not available)
        const isLocalhost = !import.meta.env.VITE_API_URL ||
                           import.meta.env.VITE_API_URL.includes('localhost') ||
                           import.meta.env.VITE_API_URL.includes('127.0.0.1');

        if (isLocalhost) {
          console.log('Backend not available; using token from URL for session.');
        } else {
          console.warn('Backend verification unavailable; using token from URL for session.', err);
        }
      }

    } catch (err) {
      setError('Authentication failed');
      console.error('Auth initialization error:', err);
      clearAuth();
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

  const refreshUser = useCallback(async () => {
    const token = getStoredToken();
    const deviceId = getDeviceId();
    if (!token || !deviceId) return;
    try {
      const response = await verifyToken();
      if (response.success && response.data?.user) {
        setUser(response.data.user);
      }
    } catch {
      // Ignore; keep current user
    }
  }, []);

  // Use window.location so we don't need useLocation (AuthProvider is outside Router)
  const pathname = typeof window !== 'undefined' ? window.location.pathname : '';
  const isPublicAuthRoute = PUBLIC_AUTH_ROUTES.includes(pathname);

  const value: AuthContextType = {
    user,
    role: user?.role || null,
    isLoading,
    isAuthenticated: !!user,
    error,
    logout,
    refreshUser,
    selectedAdminId,
    setSelectedAdminId,
  };

  // Don't block public routes (forgot-password, reset-password) — no login required
  if (isPublicAuthRoute) {
    return (
      <AuthContext.Provider value={value}>
        {children}
      </AuthContext.Provider>
    );
  }

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
  
  // Show debug info if user is not authenticated (even without error) — skip for public routes
  if (!isLoading && !user && !error && !isPublicAuthRoute) {
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
