import React from 'react';
import { useSystemLogs } from '@/hooks/useDashboardData';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ShieldAlert, Server, Monitor, Clock, UserCog, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';

export function SystemLogsTree() {
  const { data: logs, isLoading } = useSystemLogs(50);

  const getActionIcon = (action: string) => {
    const act = action.toLowerCase();
    if (act.includes('delete') || act.includes('remove')) return <ShieldAlert className="h-4 w-4 text-destructive" />;
    if (act.includes('create') || act.includes('add')) return <CheckCircle className="h-4 w-4 text-success" />;
    if (act.includes('update') || act.includes('edit')) return <UserCog className="h-4 w-4 text-blue-500" />;
    if (act.includes('login') || act.includes('open')) return <Monitor className="h-4 w-4 text-emerald-500" />;
    return <Server className="h-4 w-4 text-muted-foreground" />;
  };

  return (
    <Card className="glass-card shadow-sm h-[450px] flex flex-col w-full">
      <CardHeader className="pb-3 border-b border-border/50">
        <CardTitle className="text-lg font-bold flex items-center gap-2">
          <Server className="h-5 w-5 text-primary" />
          Global Action Audit
        </CardTitle>
        <CardDescription>Live timeline of backend actions and Dashboard history</CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-full w-full">
          {isLoading ? (
            <div className="flex flex-col gap-4 p-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex gap-4 items-start animate-pulse">
                  <div className="h-8 w-8 rounded-full bg-muted mt-1"></div>
                  <div className="space-y-2 flex-1">
                    <div className="h-4 bg-muted rounded w-3/4"></div>
                    <div className="h-3 bg-muted rounded w-1/4"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : !logs || logs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8">
              <ShieldAlert className="h-12 w-12 mb-2 opacity-20" />
              <p>No system logs recorded dynamically yet.</p>
            </div>
          ) : (
            <div className="relative border-l-2 border-border/40 ml-6 my-4 pl-6 space-y-6">
              {logs.map((log: any, idx: number) => (
                <div key={log.id || idx} className="relative group">
                  <div className="absolute -left-[35px] bg-background border border-border rounded-full p-1.5 shadow-sm ring-4 ring-background group-hover:scale-110 group-hover:ring-primary/20 transition-all">
                    {getActionIcon(log.action || '')}
                  </div>
                  
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-1">
                    <div>
                      <h4 className="font-medium text-foreground text-sm flex items-center gap-2">
                        {log.username || 'System User'}
                        <span className="text-[10px] bg-muted/80 text-muted-foreground px-2 py-0.5 rounded-full uppercase font-bold tracking-widest border border-border">
                          {log.role || 'GUEST'}
                        </span>
                      </h4>
                      <p className="text-sm text-muted-foreground mt-0.5 break-words">
                        {log.action}
                      </p>
                    </div>
                    
                    <div className="flex items-center text-xs text-muted-foreground/60 whitespace-nowrap mt-1 sm:mt-0 font-medium bg-muted/30 px-2 py-1 rounded-sm">
                      <Clock className="h-3 w-3 mr-1" />
                      {log.createdAt ? format(new Date(log.createdAt), 'MMM d, h:mm a') : 'Just now'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
