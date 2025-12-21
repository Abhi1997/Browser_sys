import React from 'react';
import { X, AlertTriangle, Info, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { mockNotifications } from '@/lib/mock-data';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';

interface NotificationsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const iconMap = {
  info: Info,
  warning: AlertTriangle,
  error: AlertCircle,
  success: CheckCircle,
};

const colorMap = {
  info: 'text-primary bg-primary/10 border-primary/30',
  warning: 'text-warning bg-warning/10 border-warning/30',
  error: 'text-destructive bg-destructive/10 border-destructive/30',
  success: 'text-success bg-success/10 border-success/30',
};

export function NotificationsPanel({ isOpen, onClose }: NotificationsPanelProps) {
  const { role } = useAuth();
  const isReadOnly = role === 'super-admin';

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="fixed right-0 top-0 h-full w-full max-w-md glass-card border-l border-border/50 z-50 animate-slide-in-right">
        <div className="flex items-center justify-between p-6 border-b border-border/50">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Notifications</h2>
            <p className="text-sm text-muted-foreground">
              {isReadOnly ? 'View only' : 'Recent alerts and updates'}
            </p>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <ScrollArea className="h-[calc(100%-88px)]">
          <div className="p-4 space-y-3">
            {mockNotifications.map((notification) => {
              const Icon = iconMap[notification.type];
              return (
                <div
                  key={notification.id}
                  className={cn(
                    "p-4 rounded-xl border transition-all duration-200",
                    colorMap[notification.type],
                    !notification.read && "ring-1 ring-inset ring-current/20"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-sm">{notification.title}</p>
                        {!notification.read && (
                          <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                            New
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm opacity-80">{notification.message}</p>
                      <p className="text-xs opacity-60 mt-2">
                        {new Date(notification.timestamp).toLocaleString()}
                      </p>
                      {notification.actionable && !isReadOnly && (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="mt-3 h-7 text-xs"
                        >
                          Take Action
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </div>
    </>
  );
}
