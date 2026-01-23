import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useActivity } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

interface ActivityTimelineChartProps {
  className?: string;
}

export function ActivityTimelineChart({ className }: ActivityTimelineChartProps) {
  const { data: activities, isLoading } = useActivity(undefined, 100);

  const formattedData = useMemo(() => {
    if (!activities || activities.length === 0) {
      return [];
    }

    // Group activities by hour for the last 24 hours
    const now = new Date();
    const hours = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date(now);
      hour.setHours(now.getHours() - (23 - i));
      hour.setMinutes(0);
      hour.setSeconds(0);
      hour.setMilliseconds(0);
      return hour;
    });

    const grouped = hours.map(hour => {
      const hourEnd = new Date(hour);
      hourEnd.setHours(hour.getHours() + 1);

      const hourActivities = activities.filter((a: any) => {
        const activityTime = new Date(a.visitStart || a.createdAt);
        return activityTime >= hour && activityTime < hourEnd;
      });

      const uniqueStudents = new Set(hourActivities.map((a: any) => a.studentId)).size;

      return {
        timestamp: hour.toISOString(),
        time: hour.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        }),
        activeStudents: uniqueStudents,
        pageViews: hourActivities.length,
        interactions: hourActivities.filter((a: any) => a.isAllowed).length,
      };
    });

    return grouped;
  }, [activities]);

  if (isLoading) {
    return (
      <div className={className}>
        <div className="glass-card p-6">
          <Skeleton className="h-[300px] w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="glass-card p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-foreground">Activity Timeline</h3>
          <p className="text-sm text-muted-foreground">Last 24 hours activity</p>
        </div>
        <div className="h-[300px]">
          {formattedData.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <p>No activity data available</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={formattedData}>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="hsl(217, 33%, 17%)" 
                vertical={false}
              />
              <XAxis 
                dataKey="time" 
                stroke="hsl(215, 20%, 55%)"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                interval={3}
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
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
              />
              <Line
                type="monotone"
                dataKey="activeStudents"
                name="Active Students"
                stroke="hsl(142, 71%, 45%)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6, fill: 'hsl(142, 71%, 45%)' }}
              />
              <Line
                type="monotone"
                dataKey="pageViews"
                name="Page Views"
                stroke="hsl(217, 91%, 60%)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6, fill: 'hsl(217, 91%, 60%)' }}
              />
              <Line
                type="monotone"
                dataKey="interactions"
                name="Interactions"
                stroke="hsl(262, 83%, 58%)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6, fill: 'hsl(262, 83%, 58%)' }}
              />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
