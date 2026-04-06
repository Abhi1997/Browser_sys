import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { formatRole, getRoleBadgeClass } from '@/lib/auth';
import { logDashboardOpen } from '@/lib/api';
import { LogOut, User, Shield, History } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { AdminSwitcher } from '@/components/super/AdminSwitcher';
import { DashboardSwitcher } from '@/components/super/DashboardSwitcher';

import { SettingsMenu } from '@/components/shared/SettingsMenu';

interface DashboardLayoutProps {
  children: React.ReactNode;
  title: string;
}

export function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const { user, role, logout } = useAuth();

  const hasLoggedOpen = useRef(false);

  // Log dashboard open (who, when) to DB for dashboard logs tab
  useEffect(() => {
    if (!user?.id || hasLoggedOpen.current) return;
    hasLoggedOpen.current = true;
    logDashboardOpen().catch(() => {});
  }, [user?.id]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-card border-b border-border/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl gradient-primary flex items-center justify-center glow-primary">
                <Shield className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">{title}</h1>
                <p className="text-sm text-muted-foreground">Educational Browser System</p>
              </div>
            </div>
            
            {(role === 'super-admin' || role === 'superuser') && (
              <div className="ml-8 flex items-center gap-4">
                <AdminSwitcher />
                {role === 'superuser' && (
                  <DashboardSwitcher />
                )}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            {/* Google Translate Widget Container */}
            <div id="google_translate_element" className="hidden lg:block overflow-hidden rounded-md h-[40px] [&>div]:h-[40px] [&_select]:h-[40px] [&_select]:border-none [&_select]:bg-muted/50 [&_select]:text-sm [&_select]:font-medium [&_select]:text-foreground relative z-50"></div>

            {/* Accessibility & Theme Settings */}
            <SettingsMenu />



            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-3 px-3">
                  <div className="h-8 w-8 rounded-lg bg-secondary flex items-center justify-center">
                    <span className="text-sm font-medium text-secondary-foreground">
                      {user?.username?.charAt(0).toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div className="text-left hidden sm:block">
                    <p className="text-sm font-medium text-foreground">{user?.username}</p>
                    <Badge variant="outline" className={`text-xs ${role ? getRoleBadgeClass(role) : ''}`}>
                      {role ? formatRole(role) : 'Unknown'}
                    </Badge>
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuItem asChild>
                  <Link to="/profile" className="flex items-center cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    My profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/history" className="flex items-center cursor-pointer">
                    <History className="mr-2 h-4 w-4" />
                    My history
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        <div className="mx-auto max-w-7xl">
          {children}
        </div>
      </main>


    </div>
  );
}
