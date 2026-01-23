import React from 'react';
import { AlertTriangle, Globe, Lock, Clock } from 'lucide-react';
import { DataTable } from '@/components/shared/DataTable';
import { Badge } from '@/components/ui/badge';
import { useViolations } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

const SEVERITY_COLORS: Record<string, string> = {
  low: 'bg-muted/20 text-muted-foreground border-muted/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  high: 'bg-destructive/20 text-destructive border-destructive/30',
  critical: 'bg-destructive/40 text-destructive border-destructive/50',
};

export function ViolationsTable({ studentId }: { studentId?: string }) {
  const { data: violations, isLoading } = useViolations(studentId, 50);

  if (isLoading) {
    return (
      <div className="glass-card p-6">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!violations || violations.length === 0) {
    return (
      <div className="glass-card p-6">
        <div className="text-center py-8">
          <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No violations found</p>
        </div>
      </div>
    );
  }

  const columns = [
    {
      key: 'student',
      header: 'Student',
      render: (item: any) => (
        <span className="font-medium text-foreground">{item.studentId}</span>
      ),
    },
    {
      key: 'type',
      header: 'Type',
      render: (item: any) => (
        <Badge variant="outline" className="text-xs">
          {item.violationType?.replace(/_/g, ' ').toUpperCase()}
        </Badge>
      ),
    },
    {
      key: 'description',
      header: 'Description',
      render: (item: any) => (
        <p className="text-sm text-foreground max-w-md truncate">{item.description}</p>
      ),
    },
    {
      key: 'url',
      header: 'Attempted URL',
      render: (item: any) => (
        <a 
          href={item.attemptedUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-xs text-primary hover:underline truncate max-w-xs block"
        >
          {item.attemptedUrl}
        </a>
      ),
    },
    {
      key: 'mode',
      header: 'Mode',
      render: (item: any) => (
        <Badge variant="outline" className="text-xs">
          {item.currentMode?.toUpperCase() || 'N/A'}
        </Badge>
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (item: any) => (
        <Badge variant="outline" className={SEVERITY_COLORS[item.severity] || ''}>
          {item.severity?.toUpperCase() || 'UNKNOWN'}
        </Badge>
      ),
    },
    {
      key: 'time',
      header: 'Time',
      render: (item: any) => (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          {item.createdAt ? new Date(item.createdAt).toLocaleString() : 'N/A'}
        </div>
      ),
    },
  ];

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Security Violations</h3>
          <p className="text-sm text-muted-foreground">
            {studentId ? 'Violations for this student' : 'All security violations'}
          </p>
        </div>
        <Badge variant="outline" className="bg-warning/20 text-warning">
          {violations.length} Total
        </Badge>
      </div>
      <DataTable
        data={violations}
        columns={columns as any}
        emptyMessage="No violations found"
      />
    </div>
  );
}

