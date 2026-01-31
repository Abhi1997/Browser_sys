import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Crown, Building2, GraduationCap, ChevronDown, LayoutDashboard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/contexts/AuthContext';

const DASHBOARDS = [
  { path: '/dashboard-superuser', label: 'Superuser Dashboard', desc: 'Full access – view & edit all', icon: Crown, role: 'superuser' },
  { path: '/dashboard-admin', label: 'Admin Dashboard', desc: 'View as admin', icon: Building2, role: 'admin' },
  { path: '/dashboard-teacher', label: 'Teacher Dashboard', desc: 'View as teacher', icon: GraduationCap, role: 'teacher' },
] as const;

export function DashboardSwitcher() {
  const { role } = useAuth();
  const location = useLocation();
  const current = DASHBOARDS.find((d) => d.path === location.pathname) ?? DASHBOARDS[0];

  if (role !== 'superuser') return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2 min-w-[180px] justify-between bg-amber-500/5 border-amber-500/30">
          <div className="flex items-center gap-2">
            <LayoutDashboard className="h-4 w-4 text-amber-600" />
            <span className="truncate max-w-[140px]">{current.label}</span>
          </div>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[260px]">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Crown className="h-4 w-4 text-amber-600" />
          View dashboard
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {DASHBOARDS.map((d) => {
          const Icon = d.icon;
          const isActive = location.pathname === d.path;
          return (
            <DropdownMenuItem key={d.path} asChild>
              <Link to={d.path} className="flex items-center gap-2 cursor-pointer">
                <Icon className="h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <p className="font-medium">{d.label}</p>
                  <p className="text-xs text-muted-foreground">{d.desc}</p>
                </div>
                {isActive && (
                  <span className="h-2 w-2 rounded-full bg-amber-500" aria-hidden />
                )}
              </Link>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
