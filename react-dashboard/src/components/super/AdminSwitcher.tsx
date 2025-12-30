import React, { useMemo } from 'react';
import { Check, ChevronDown, Building2, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { useUsers } from '@/hooks/useDashboardData';
import { AdminStats } from '@/lib/types';

export function AdminSwitcher() {
  const { selectedAdminId, setSelectedAdminId } = useAuth();
  const { data: users } = useUsers();

  const adminStats = useMemo((): AdminStats[] => {
    if (!users) return [];

    // Group by admin (for now, we'll create a single "institution" from all admins)
    const adminUsers = users.filter((u: any) => u.role === 'admin' || u.role === 'super-admin');
    
    if (adminUsers.length === 0) return [];

    // Create a single admin stat entry representing the system
    const activeUsers = users.filter((u: any) => u.isActive);
    const teacherUsers = users.filter((u: any) => u.role === 'teacher');
    const studentUsers = users.filter((u: any) => u.role === 'student');

    return [{
      id: 'system',
      adminId: 'system',
      adminName: 'System Overview',
      totalUsers: users.length,
      activeUsers: activeUsers.length,
      teachers: teacherUsers.length,
      students: studentUsers.length,
      activeSessions: 0,
    }];
  }, [users]);
  
  const selectedAdmin = selectedAdminId 
    ? adminStats.find(a => a.adminId === selectedAdminId)
    : null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2 min-w-[200px] justify-between">
          <div className="flex items-center gap-2">
            {selectedAdmin ? (
              <>
                <Building2 className="h-4 w-4 text-primary" />
                <span className="truncate max-w-[120px]">{selectedAdmin.adminName}</span>
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 text-accent" />
                <span>Global Overview</span>
              </>
            )}
          </div>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[280px]">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Eye className="h-4 w-4" />
          View Context
          <Badge variant="outline" className="ml-auto text-[10px] bg-accent/20 text-accent border-accent/30">
            Read Only
          </Badge>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        <DropdownMenuItem 
          onClick={() => setSelectedAdminId(null)}
          className="gap-2"
        >
          <Eye className="h-4 w-4 text-accent" />
          <div className="flex-1">
            <p className="font-medium">Global Overview</p>
            <p className="text-xs text-muted-foreground">All institutions</p>
          </div>
          {!selectedAdminId && <Check className="h-4 w-4 text-primary" />}
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        <DropdownMenuLabel className="text-xs text-muted-foreground">
          Institutions
        </DropdownMenuLabel>
        
        {adminStats.map((admin) => (
          <DropdownMenuItem
            key={admin.adminId}
            onClick={() => setSelectedAdminId(admin.adminId)}
            className="gap-2"
          >
            <Building2 className="h-4 w-4 text-primary" />
            <div className="flex-1">
              <p className="font-medium">{admin.adminName}</p>
              <p className="text-xs text-muted-foreground">
                {admin.totalUsers} users • {admin.activeSessions} active
              </p>
            </div>
            {selectedAdminId === admin.adminId && <Check className="h-4 w-4 text-primary" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
