import React from 'react';
import { Shield, Loader2 } from 'lucide-react';

export default function Loading() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center animate-fade-in">
        <div className="relative mb-8">
          <div className="h-20 w-20 mx-auto rounded-2xl gradient-primary flex items-center justify-center glow-primary animate-pulse-slow">
            <Shield className="h-10 w-10 text-primary-foreground" />
          </div>
          <div className="absolute -bottom-2 left-1/2 -translate-x-1/2">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        </div>
        
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Authenticating
        </h2>
        <p className="text-muted-foreground">
          Verifying your credentials...
        </p>
      </div>
    </div>
  );
}
