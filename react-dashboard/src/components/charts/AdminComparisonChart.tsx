import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { mockAdminStats } from '@/lib/mock-data';

interface AdminComparisonChartProps {
  data?: typeof mockAdminStats;
  className?: string;
}

export function AdminComparisonChart({ data = mockAdminStats, className }: AdminComparisonChartProps) {
  const chartData = data.map(admin => ({
    name: admin.adminName.split(' ')[0], // Shorten name
    fullName: admin.adminName,
    teachers: admin.teachers,
    students: admin.students,
    activeSessions: admin.activeSessions,
  }));

  return (
    <div className={className}>
      <div className="glass-card p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-foreground">Admin Comparison</h3>
          <p className="text-sm text-muted-foreground">Users per institution</p>
        </div>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} barCategoryGap="20%">
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="hsl(217, 33%, 17%)" 
                vertical={false}
              />
              <XAxis 
                dataKey="name" 
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
                labelFormatter={(value, payload) => {
                  const item = payload?.[0]?.payload;
                  return item?.fullName || value;
                }}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
              />
              <Bar 
                dataKey="teachers" 
                name="Teachers"
                fill="hsl(142, 71%, 45%)" 
                radius={[4, 4, 0, 0]}
              />
              <Bar 
                dataKey="students" 
                name="Students"
                fill="hsl(262, 83%, 58%)" 
                radius={[4, 4, 0, 0]}
              />
              <Bar 
                dataKey="activeSessions" 
                name="Active Sessions"
                fill="hsl(217, 91%, 60%)" 
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
