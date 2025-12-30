import React, { useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useActivity } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

interface LoginActivityChartProps {
  className?: string;
}

export function LoginActivityChart({ className }: LoginActivityChartProps) {
  const { data: activity, isLoading } = useActivity(undefined, 50);
  
  const formattedData = useMemo(() => {
    if (!activity) return [];
    
    // Group by date
    const grouped = activity.reduce((acc: any, item: any) => {
      const date = new Date(item.visitStart || item.createdAt).toLocaleDateString();
      if (!acc[date]) {
        acc[date] = { date, logins: 0, uniqueUsers: new Set() };
      }
      acc[date].logins++;
      acc[date].uniqueUsers.add(item.studentId || item.userId);
      return acc;
    }, {});
    
    return Object.values(grouped).map((item: any) => ({
      ...item,
      uniqueUsers: item.uniqueUsers.size,
      date: new Date(item.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
    })).slice(-7); // Last 7 days
  }, [activity]);

  if (isLoading) {
    return (
      <div className={className}>
        <div className="glass-card p-6">
          <Skeleton className="h-8 w-48 mb-6" />
          <Skeleton className="h-[300px] w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="glass-card p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-foreground">Login Activity</h3>
          <p className="text-sm text-muted-foreground">Daily logins over the past week</p>
        </div>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={formattedData.length > 0 ? formattedData : [{ date: 'No data', logins: 0, uniqueUsers: 0 }]}>
              <defs>
                <linearGradient id="loginGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="usersGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(262, 83%, 58%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(262, 83%, 58%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="hsl(217, 33%, 17%)" 
                vertical={false}
              />
              <XAxis 
                dataKey="date" 
                stroke="hsl(215, 20%, 55%)"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                stroke="hsl(215, 20%, 55%)"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(222, 47%, 8%)',
                  border: '1px solid hsl(217, 33%, 17%)',
                  borderRadius: '12px',
                  boxShadow: '0 4px 24px -4px rgba(0,0,0,0.5)',
                }}
                labelStyle={{ color: 'hsl(210, 40%, 98%)' }}
                itemStyle={{ color: 'hsl(215, 20%, 55%)' }}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
              />
              <Area
                type="monotone"
                dataKey="logins"
                name="Total Logins"
                stroke="hsl(217, 91%, 60%)"
                strokeWidth={2}
                fill="url(#loginGradient)"
              />
              <Area
                type="monotone"
                dataKey="uniqueUsers"
                name="Unique Users"
                stroke="hsl(262, 83%, 58%)"
                strokeWidth={2}
                fill="url(#usersGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
