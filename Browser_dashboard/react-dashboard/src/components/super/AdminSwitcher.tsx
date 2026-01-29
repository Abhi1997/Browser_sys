import React from 'react';
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
import { useAdmins } from '@/hooks/useDashboardData';

export function AdminSwitcher() {
  const { selectedAdminId, setSelectedAdminId } = useAuth();
  const { data: admins, isLoading } = useAdmins();

  const adminList = (admins ?? []) as any[];
  const selectedAdmin = selectedAdminId === 'system' || !selectedAdminId
    ? { id: 'system', adminName: 'System Overview' }
    : adminList.find((a: any) => String(a.id) === selectedAdminId);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2 min-w-[200px] justify-between">
          <div className="flex items-center gap-2">
            {selectedAdmin ? (
              <>
                <Building2 className="h-4 w-4 text-primary" />
                <span className="truncate max-w-[120px]">
                  {selectedAdmin.adminName ?? selectedAdmin.username ?? 'System Overview'}
                </span>
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 text-accent" />
                <span>System Overview</span>
              </>
            )}
          </div>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[280px]">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Eye className="h-4 w-4" />
          Monitor admins
          <Badge variant="outline" className="ml-auto text-[10px] bg-accent/20 text-accent border-accent/30">
            Read Only
          </Badge>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={() => setSelectedAdminId('system')}
          className="gap-2"
        >
          <Eye className="h-4 w-4 text-accent" />
          <div className="flex-1">
            <p className="font-medium">System Overview</p>
            <p className="text-xs text-muted-foreground">All admins & data</p>
          </div>
          {(selectedAdminId === 'system' || !selectedAdminId) && <Check className="h-4 w-4 text-primary" />}
        </DropdownMenuItem>

        <DropdownMenuSeparator />
        <DropdownMenuLabel className="text-xs text-muted-foreground">
          Admins (from database)
        </DropdownMenuLabel>

        {isLoading ? (
          <div className="p-4 text-sm text-muted-foreground">Loading admins…</div>
        ) : (
          adminList.map((admin: any) => (
            <DropdownMenuItem
              key={admin.id}
              onClick={() => setSelectedAdminId(String(admin.id))}
              className="gap-2"
            >
              <Building2 className="h-4 w-4 text-primary" />
              <div className="flex-1">
                <p className="font-medium">{admin.username}</p>
                <p className="text-xs text-muted-foreground">{admin.email ?? admin.gmail ?? 'Admin'}</p>
              </div>
              {selectedAdminId === String(admin.id) && <Check className="h-4 w-4 text-primary" />}
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
