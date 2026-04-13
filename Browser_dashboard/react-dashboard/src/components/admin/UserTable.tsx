import React from 'react';
import { User as UserIcon, MoreHorizontal, UserX, UserCheck, Pencil, Trash2 } from 'lucide-react';
import { DataTable } from '@/components/shared/DataTable';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { User } from '@/lib/types';
import { formatRole, getRoleBadgeClass } from '@/lib/auth';
import { useUsers, useToggleUserStatus, useDeleteUser } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

interface UserTableProps {
  readOnly?: boolean;
}

export function UserTable({ readOnly = false }: UserTableProps) {
  const { data: users, isLoading } = useUsers();
  const toggleStatus = useToggleUserStatus();
  const deleteUser = useDeleteUser();

  const [searchTerm, setSearchTerm] = React.useState('');
  const [searchColumn, setSearchColumn] = React.useState('all');
  const [sortConfig, setSortConfig] = React.useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  const handleToggleStatus = (userId: string) => {
    toggleStatus.mutate(userId);
  };

  const handleDelete = (userId: string) => {
    if (window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      deleteUser.mutate(userId);
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

  const processedUsers = React.useMemo(() => {
    if (!users) return [];
    
    // Filter
    let result = users.filter((u: User) => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      
      switch (searchColumn) {
        case 'username':
          return u.username.toLowerCase().includes(term);
        case 'email':
          return u.email.toLowerCase().includes(term);
        case 'role':
          return u.role.toLowerCase().includes(term);
        case 'all':
        default:
          return (
            u.username.toLowerCase().includes(term) ||
            u.email.toLowerCase().includes(term) ||
            u.role.toLowerCase().includes(term)
          );
      }
    });

    // Sort
    if (sortConfig) {
      result = [...result].sort((a, b) => {
        let valA, valB;
        switch (sortConfig.key) {
          case 'username':
            valA = a.username.toLowerCase(); valB = b.username.toLowerCase(); break;
          case 'role':
            valA = a.role; valB = b.role; break;
          case 'status':
            valA = a.isActive ? 1 : 0; valB = b.isActive ? 1 : 0; break;
          case 'lastLogin':
            valA = a.lastLogin ? new Date(a.lastLogin).getTime() : 0;
            valB = b.lastLogin ? new Date(b.lastLogin).getTime() : 0;
            break;
          case 'createdAt':
            valA = new Date(a.createdAt).getTime();
            valB = new Date(b.createdAt).getTime();
            break;
          default:
            return 0;
        }
        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return result;
  }, [users, searchTerm, sortConfig]);

  if (isLoading) {
    return (
      <div className="glass-card p-6">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!users || users.length === 0) {
    return (
      <div className="glass-card p-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground">No users found</p>
        </div>
      </div>
    );
  }

  const columns = [
    {
      key: 'username',
      header: (
        <Button variant="ghost" onClick={() => handleSort('username')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          User <SortIcon columnKey="username" />
        </Button>
      ),
      render: (item: User) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center">
            <UserIcon className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <p className="font-medium text-foreground">{item.username}</p>
            <p className="text-xs text-muted-foreground">{item.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'role',
      header: (
        <Button variant="ghost" onClick={() => handleSort('role')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Role <SortIcon columnKey="role" />
        </Button>
      ),
      render: (item: User) => (
        <Badge variant="outline" className={getRoleBadgeClass(item.role)}>
          {formatRole(item.role)}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: (
        <Button variant="ghost" onClick={() => handleSort('status')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Status <SortIcon columnKey="status" />
        </Button>
      ),
      render: (item: User) => (
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
      key: 'lastLogin',
      header: (
        <Button variant="ghost" onClick={() => handleSort('lastLogin')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Last Login <SortIcon columnKey="lastLogin" />
        </Button>
      ),
      render: (item: User) => (
        <span className="text-muted-foreground text-sm">
          {item.lastLogin 
            ? new Date(item.lastLogin).toLocaleDateString()
            : 'Never'
          }
        </span>
      ),
    },
    {
      key: 'createdAt',
      header: (
        <Button variant="ghost" onClick={() => handleSort('createdAt')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Created <SortIcon columnKey="createdAt" />
        </Button>
      ),
      render: (item: User) => (
        <span className="text-muted-foreground text-sm">
          {new Date(item.createdAt).toLocaleDateString()}
        </span>
      ),
    },
    ...(readOnly ? [] : [{
      key: 'actions',
      header: '',
      render: (item: User) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Pencil className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleToggleStatus(item.id)}>
              {item.isActive ? (
                <>
                  <UserX className="mr-2 h-4 w-4" />
                  Disable
                </>
              ) : (
                <>
                  <UserCheck className="mr-2 h-4 w-4" />
                  Enable
                </>
              )}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {!['admin', 'superadmin', 'superuser'].includes(item.role.toLowerCase()) && (
              <DropdownMenuItem 
                onClick={() => handleDelete(item.id)}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    }]),
  ];

  return (
    <div className="glass-card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Users</h3>
          <p className="text-sm text-muted-foreground">Manage user accounts</p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <div className="flex shadow-sm rounded-md grow group">
            <Select value={searchColumn} onValueChange={setSearchColumn}>
              <SelectTrigger className="w-[130px] rounded-r-none border-r-0 focus:ring-0 focus:border-input bg-muted/50 transition-colors hover:bg-muted font-medium cursor-pointer">
                <SelectValue placeholder="Filter by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Fields</SelectItem>
                <SelectItem value="username">Name</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="role">Role</SelectItem>
              </SelectContent>
            </Select>
            <div className="relative w-full sm:w-56 group-hover:border-primary/50 transition-colors">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
              <Input
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 rounded-l-none border-l-0 focus-visible:ring-1 focus-visible:ring-offset-0 focus-visible:border-primary transition-all"
              />
            </div>
          </div>
        </div>
      </div>
      <DataTable
        data={processedUsers}
        columns={columns as any}
        emptyMessage="No users found"
      />
    </div>
  );
}
