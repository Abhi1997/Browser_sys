import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getStoredToken, isTokenExpired, clearAuth } from '@/lib/auth';
import { verifyToken } from '@/lib/api';
import Loading from '@/pages/Loading';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isLoading, isAuthenticated, error } = useAuth();
  const location = useLocation();
  const [isVerifying, setIsVerifying] = React.useState(false);

    // Verify token on route access (optional - only in production)
    useEffect(() => {
      const verifyTokenOnAccess = async () => {
        const token = getStoredToken();
        
        if (!token) {
          return;
        }

        // Check expiry
        if (isTokenExpired(token)) {
          clearAuth();
          return;
        }

        // Skip backend verification for localhost (local development)
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
        const isLocalhost = apiUrl.includes('localhost') || apiUrl.includes('127.0.0.1');
        
        if (isLocalhost) {
          // Local development - skip backend verification
          return;
        }

        // Production mode - attempt verification (but don't block if it fails)
        setIsVerifying(true);
        try {
          const response = await verifyToken();
          if (!response.success) {
            // Log but don't block - continue with token authentication
            console.warn('Backend verification failed, continuing with token:', response.error);
          }
        } catch (err) {
          // Network error - continue with token
          console.log('Backend not available, continuing with token authentication');
        } finally {
          setIsVerifying(false);
        }
      };

      if (isAuthenticated && !isLoading) {
        verifyTokenOnAccess();
      }
    }, [location.pathname, isAuthenticated, isLoading]);

  if (isLoading || isVerifying) {
    return <Loading />;
  }

  if (error) {
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
          Please login again to access the dashboard.
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}
