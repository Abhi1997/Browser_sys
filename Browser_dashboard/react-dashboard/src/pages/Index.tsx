import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import Loading from './Loading';

const Index = () => {
  const navigate = useNavigate();
  const { isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        // Redirect to admin dashboard by default (any authenticated user can access any dashboard)
        navigate('/dashboard-admin', { replace: true });
      } else {
        navigate('/unauthorized', { replace: true });
      }
    }
  }, [isLoading, isAuthenticated, navigate]);

  return <Loading />;
};

export default Index;
