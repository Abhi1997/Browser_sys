import React from 'react';
import { ShieldX, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { getQueryParams } from '@/lib/auth';

export default function Unauthorized() {
  const { user, role, isLoading, isAuthenticated, error } = useAuth();
  const params = getQueryParams();
  const hasToken = !!params.token;
  const hasDeviceId = !!params.deviceId;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="max-w-md text-center animate-slide-up">
        <div className="h-24 w-24 mx-auto rounded-2xl bg-destructive/10 flex items-center justify-center mb-8 animate-float">
          <ShieldX className="h-12 w-12 text-destructive" />
        </div>
        
        <h1 className="text-3xl font-bold text-foreground mb-4">
          Access Denied
        </h1>
        
        <p className="text-muted-foreground mb-8">
          You don't have permission to access this page. This could be because:
        </p>
        
        <ul className="text-left text-sm text-muted-foreground space-y-2 mb-8 glass-card p-4">
          <li className="flex items-start gap-2">
            <span className="text-destructive">•</span>
            Your session has expired
          </li>
          <li className="flex items-start gap-2">
            <span className="text-destructive">•</span>
            You don't have the required role
          </li>
          <li className="flex items-start gap-2">
            <span className="text-destructive">•</span>
            Your device ID doesn't match
          </li>
          <li className="flex items-start gap-2">
            <span className="text-destructive">•</span>
            Students are not allowed dashboard access
          </li>
        </ul>

        {/* Debug Information */}
        <div className="mb-8 glass-card p-4 text-left">
          <p className="text-sm font-semibold text-foreground mb-2">
            Debug Information:
          </p>
          <div className="text-xs text-muted-foreground font-mono space-y-1">
            <div>User: {user ? user.username : 'Not loaded'}</div>
            <div>Role: {role || 'Not set'}</div>
            <div>Authenticated: {isAuthenticated ? 'Yes' : 'No'}</div>
            <div>Loading: {isLoading ? 'Yes' : 'No'}</div>
            <div>Token in URL: {hasToken ? 'Yes' : 'No'}</div>
            <div>Device ID in URL: {hasDeviceId ? 'Yes' : 'No'}</div>
            {error && <div className="text-destructive">Error: {error}</div>}
          </div>
        </div>
        
        <Button 
          variant="outline" 
          className="gap-2"
          onClick={() => window.history.back()}
        >
          <ArrowLeft className="h-4 w-4" />
          Go Back
        </Button>
      </div>
    </div>
  );
}
