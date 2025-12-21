import React, { useState } from 'react';
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
import { mockUsers } from '@/lib/mock-data';
import { User } from '@/lib/types';
import { formatRole, getRoleBadgeClass } from '@/lib/auth';
import { toast } from '@/hooks/use-toast';

interface UserTableProps {
  readOnly?: boolean;
}

export function UserTable({ readOnly = false }: UserTableProps) {
  const [users, setUsers] = useState(mockUsers);

  const handleToggleStatus = (userId: string) => {
    setUsers(prev => prev.map(user => 
      user.id === userId ? { ...user, isActive: !user.isActive } : user
    ));
    toast({
      title: 'User status updated',
      description: 'The user account status has been changed.',
    });
  };

  const handleDelete = (userId: string) => {
    setUsers(prev => prev.filter(user => user.id !== userId));
    toast({
      title: 'User removed',
      description: 'The user has been removed from the system.',
      variant: 'destructive',
    });
  };

  const columns = [
    {
      key: 'username',
      header: 'User',
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
      header: 'Role',
      render: (item: User) => (
        <Badge variant="outline" className={getRoleBadgeClass(item.role)}>
          {formatRole(item.role)}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
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
      header: 'Last Login',
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
      header: 'Created',
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
            <DropdownMenuItem 
              onClick={() => handleDelete(item.id)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    }]),
  ];

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Users</h3>
          <p className="text-sm text-muted-foreground">Manage user accounts</p>
        </div>
        {!readOnly && (
          <Button className="gap-2">
            <UserIcon className="h-4 w-4" />
            Add User
          </Button>
        )}
      </div>
      <DataTable
        data={users}
        columns={columns as any}
        emptyMessage="No users found"
      />
    </div>
  );
}
