import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import Loading from './Loading';

const Index = () => {
  const navigate = useNavigate();
  const { isLoading, isAuthenticated, user } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && user) {
        // Redirect based on role
        const role = user.role?.toLowerCase();
        if (role === 'superuser') {
          navigate('/dashboard-superuser', { replace: true });
        } else if (role === 'superadmin' || role === 'super-admin') {
          navigate('/dashboard-superadmin', { replace: true });
        } else if (role === 'admin') {
          navigate('/dashboard-admin', { replace: true });
        } else if (role === 'teacher') {
          navigate('/dashboard-teacher', { replace: true });
        } else {
          // Student or unknown - go to history/profile
          navigate('/history', { replace: true });
        }
      } else if (isAuthenticated) {
        // Authenticated but no user info - default to admin dashboard
        navigate('/dashboard-admin', { replace: true });
      } else {
        navigate('/unauthorized', { replace: true });
      }
    }
  }, [isLoading, isAuthenticated, user, navigate]);

  return <Loading />;
};

export default Index;
