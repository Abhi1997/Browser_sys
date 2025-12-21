import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getRoleDashboardPath } from '@/lib/auth';
import Loading from './Loading';

const Index = () => {
  const navigate = useNavigate();
  const { role, isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && role) {
        const dashboardPath = getRoleDashboardPath(role);
        navigate(dashboardPath, { replace: true });
      } else {
        navigate('/unauthorized', { replace: true });
      }
    }
  }, [isLoading, isAuthenticated, role, navigate]);

  return <Loading />;
};

export default Index;
