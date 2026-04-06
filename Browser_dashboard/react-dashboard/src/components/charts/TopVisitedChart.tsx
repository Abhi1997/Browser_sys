import React from 'react';
import { useTopSites } from '@/hooks/useDashboardData';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Globe, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function TopVisitedChart() {
  const { data: topSites, isLoading, refetch, isFetching } = useTopSites();

  // Color palette for the bars based on position
  const colors = [
    'hsl(var(--primary))',
    'hsl(var(--primary) / 0.8)',
    'hsl(var(--primary) / 0.7)',
    'hsl(var(--primary) / 0.6)',
    'hsl(var(--primary) / 0.5)',
    'hsl(var(--primary) / 0.4)',
    'hsl(var(--primary) / 0.3)',
  ];

  return (
    <Card className="glass-card shadow-sm h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="flex items-center gap-2 text-lg font-bold">
            <Globe className="h-5 w-5 text-primary" />
            Top Visited Sites
          </CardTitle>
          <CardDescription>Most accessed domains ecosystem-wide</CardDescription>
        </div>
        <Button 
          variant="outline" 
          size="icon" 
          className="h-8 w-8" 
          onClick={() => refetch()}
          disabled={isFetching}
        >
          <RefreshCcw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
        </Button>
      </CardHeader>
      <CardContent className="flex-1 min-h-[300px] mt-4">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : !topSites || topSites.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-muted-foreground pb-8">
            <Globe className="h-12 w-12 mb-3 opacity-20" />
            <p>No browsing data available yet</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={topSites}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
              <XAxis 
                type="number" 
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                tickLine={false}
              />
              <YAxis 
                dataKey="domain" 
                type="category" 
                width={120} 
                tick={{ fill: 'hsl(var(--foreground))', fontSize: 13 }}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: 'hsl(var(--muted))', opacity: 0.4 }}
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  borderColor: 'hsl(var(--border))',
                  borderRadius: '8px',
                  color: 'hsl(var(--foreground))',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
                formatter={(value: number) => [`${value} Visits`, 'Total Activity']}
                labelStyle={{ fontWeight: 'bold', marginBottom: '8px', color: 'hsl(var(--foreground))' }}
              />
              <Bar 
                dataKey="visits" 
                radius={[0, 4, 4, 0]}
                barSize={24}
                animationDuration={1500}
              >
                {topSites.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
