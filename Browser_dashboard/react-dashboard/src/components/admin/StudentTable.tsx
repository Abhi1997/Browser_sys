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
import { Input } from '@/components/ui/input';
import { useAuth } from '@/contexts/AuthContext';
import { Search, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

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
  
  const [searchTerm, setSearchTerm] = React.useState('');
  const [searchColumn, setSearchColumn] = React.useState('all');
  const [sortConfig, setSortConfig] = React.useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  const handleModeChange = (studentId: string, newMode: string) => {
    if (user?.id) {
      updateMode.mutate({
        studentId,
        mode: newMode,
        changedBy: parseInt(user.id),
      });
    }
  };

  const handleSort = (key: string) => {
    setSortConfig(current => {
      if (current?.key === key) {
        if (current.direction === 'asc') return { key, direction: 'desc' };
        return null;
      }
      return { key, direction: 'asc' };
    });
  };

  const SortIcon = ({ columnKey }: { columnKey: string }) => {
    if (sortConfig?.key !== columnKey) return <ArrowUpDown className="ml-2 h-4 w-4 text-muted-foreground/50" />;
    return sortConfig.direction === 'asc' 
      ? <ArrowUp className="ml-2 h-4 w-4 text-primary" /> 
      : <ArrowDown className="ml-2 h-4 w-4 text-primary" />;
  };

  const processedStudents = React.useMemo(() => {
    if (!students) return [];
    
    // Filter
    let result = students.filter((s: any) => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      
      switch (searchColumn) {
        case 'studentId':
          return s.studentId?.toLowerCase().includes(term);
        case 'gmail':
          return s.gmail?.toLowerCase().includes(term);
        case 'mode':
          return s.assignedMode?.toLowerCase().includes(term);
        case 'all':
        default:
          return (
            s.studentId?.toLowerCase().includes(term) ||
            s.gmail?.toLowerCase().includes(term) ||
            s.assignedMode?.toLowerCase().includes(term)
          );
      }
    });

    // Sort
    if (sortConfig) {
      result = [...result].sort((a, b) => {
        let valA, valB;
        switch (sortConfig.key) {
          case 'student':
            valA = a.studentId?.toLowerCase(); valB = b.studentId?.toLowerCase(); break;
          case 'mode':
            valA = a.assignedMode; valB = b.assignedMode; break;
          case 'violations':
            valA = a.violationCount || 0; valB = b.violationCount || 0; break;
          case 'status':
            valA = a.isActive ? 1 : 0; valB = b.isActive ? 1 : 0; break;
          default:
            return 0;
        }
        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return result;
  }, [students, searchTerm, sortConfig]);

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
      header: (
        <Button variant="ghost" onClick={() => handleSort('student')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Student <SortIcon columnKey="student" />
        </Button>
      ),
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
      header: (
        <Button variant="ghost" onClick={() => handleSort('mode')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Mode <SortIcon columnKey="mode" />
        </Button>
      ),
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
      header: (
        <Button variant="ghost" onClick={() => handleSort('violations')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Violations <SortIcon columnKey="violations" />
        </Button>
      ),
      render: (item: any) => (
        <span className={`text-sm ${item.violationCount > 0 ? 'text-warning' : 'text-muted-foreground'}`}>
          {item.violationCount || 0}
        </span>
      ),
    },
    {
      key: 'status',
      header: (
        <Button variant="ghost" onClick={() => handleSort('status')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Status <SortIcon columnKey="status" />
        </Button>
      ),
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Students</h3>
          <p className="text-sm text-muted-foreground">Manage student modes and monitor activity</p>
        </div>
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <div className="flex shadow-sm rounded-md grow group">
            <Select value={searchColumn} onValueChange={setSearchColumn}>
              <SelectTrigger className="w-[130px] rounded-r-none border-r-0 focus:ring-0 focus:border-input bg-muted/50 transition-colors hover:bg-muted font-medium cursor-pointer">
                <SelectValue placeholder="Filter by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Fields</SelectItem>
                <SelectItem value="studentId">Student ID</SelectItem>
                <SelectItem value="gmail">Email</SelectItem>
                <SelectItem value="mode">Mode</SelectItem>
              </SelectContent>
            </Select>
            <div className="relative w-full sm:w-56 group-hover:border-primary/50 transition-colors">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
              <Input
                placeholder="Search students..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 rounded-l-none border-l-0 focus-visible:ring-1 focus-visible:ring-offset-0 focus-visible:border-primary transition-all"
              />
            </div>
          </div>
        </div>
      </div>
      <DataTable
        data={processedStudents}
        columns={columns as any}
        emptyMessage="No students found"
      />
    </div>
  );
}

