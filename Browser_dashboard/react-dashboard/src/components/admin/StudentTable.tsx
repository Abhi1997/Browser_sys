import React from 'react';
import { User as UserIcon, MoreHorizontal, Folder, BookOpen, AlertCircle, Globe } from 'lucide-react';
import { DataTable } from '@/components/shared/DataTable';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useStudents, useUpdateStudentMode } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useAuth } from '@/contexts/AuthContext';

const MODE_COLORS: Record<string, string> = {
  cached: 'bg-violet-500/20 text-violet-700 border-violet-500/30',
  study: 'bg-primary/20 text-primary border-primary/30',
  restricted: 'bg-warning/20 text-warning border-warning/30',
  free: 'bg-success/20 text-success border-success/30',
};

const MODE_ICONS: Record<string, any> = {
  cached: Folder,
  study: BookOpen,
  restricted: AlertCircle,
  free: Globe,
};

export function StudentTable() {
  const { data: students, isLoading } = useStudents();
  const { user } = useAuth();
  const updateMode = useUpdateStudentMode();

  const handleModeChange = (studentId: string, newMode: string) => {
    if (user?.id) {
      updateMode.mutate({
        studentId,
        mode: newMode,
        changedBy: parseInt(user.id),
      });
    }
  };

  if (isLoading) {
    return (
      <div className="glass-card p-6">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!students || students.length === 0) {
    return (
      <div className="glass-card p-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground">No students found</p>
        </div>
      </div>
    );
  }

  const columns = [
    {
      key: 'student',
      header: 'Student',
      render: (item: any) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center">
            <UserIcon className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <p className="font-medium text-foreground">{item.studentId}</p>
            <p className="text-xs text-muted-foreground">{item.gmail}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'mode',
      header: 'Mode',
      render: (item: any) => {
        const ModeIcon = MODE_ICONS[item.assignedMode] || AlertCircle;
        return (
          <div className="flex items-center gap-2">
            <ModeIcon className="h-4 w-4" />
            <Badge variant="outline" className={MODE_COLORS[item.assignedMode] || ''}>
              {item.assignedMode?.toUpperCase() || 'UNKNOWN'}
            </Badge>
          </div>
        );
      },
    },
    {
      key: 'violations',
      header: 'Violations',
      render: (item: any) => (
        <span className={`text-sm ${item.violationCount > 0 ? 'text-warning' : 'text-muted-foreground'}`}>
          {item.violationCount || 0}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item: any) => (
        <Badge variant={item.isActive ? 'default' : 'secondary'} className={
          item.isActive 
            ? 'bg-success/20 text-success border-success/30' 
            : 'bg-muted text-muted-foreground'
        }>
          {item.isActive ? 'Active' : 'Disabled'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Change Mode',
      render: (item: any) => (
        <Select
          value={item.assignedMode}
          onValueChange={(value) => handleModeChange(item.studentId, value)}
        >
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="cached">Cached</SelectItem>
            <SelectItem value="study">Study</SelectItem>
            <SelectItem value="restricted">Restricted</SelectItem>
            <SelectItem value="free">Free</SelectItem>
          </SelectContent>
        </Select>
      ),
    },
  ];

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Students</h3>
          <p className="text-sm text-muted-foreground">Manage student modes and monitor activity</p>
        </div>
      </div>
      <DataTable
        data={students}
        columns={columns as any}
        emptyMessage="No students found"
      />
    </div>
  );
}

