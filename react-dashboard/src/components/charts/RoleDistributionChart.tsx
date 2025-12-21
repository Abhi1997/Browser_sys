import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { mockStatsOverview } from '@/lib/mock-data';

interface RoleDistributionChartProps {
  data?: typeof mockStatsOverview.usersByRole;
  className?: string;
}

const COLORS = [
  'hsl(217, 91%, 60%)',  // Primary - Admin
  'hsl(142, 71%, 45%)',  // Success - Teacher
  'hsl(262, 83%, 58%)',  // Accent - Student
];

export function RoleDistributionChart({ 
  data = mockStatsOverview.usersByRole, 
  className 
}: RoleDistributionChartProps) {
  const chartData = [
    { name: 'Admins', value: data.admin, color: COLORS[0] },
    { name: 'Teachers', value: data.teacher, color: COLORS[1] },
    { name: 'Students', value: data.student, color: COLORS[2] },
  ];

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className={className}>
      <div className="glass-card p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-foreground">User Distribution</h3>
          <p className="text-sm text-muted-foreground">Users by role</p>
        </div>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={4}
                dataKey="value"
                stroke="hsl(222, 47%, 8%)"
                strokeWidth={2}
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color}
                    style={{
                      filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.3))',
                    }}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(222, 47%, 8%)',
                  border: '1px solid hsl(217, 33%, 17%)',
                  borderRadius: '12px',
                  boxShadow: '0 4px 24px -4px rgba(0,0,0,0.5)',
                }}
                labelStyle={{ color: 'hsl(210, 40%, 98%)' }}
                formatter={(value: number) => [`${value} users (${((value / total) * 100).toFixed(1)}%)`, '']}
              />
              <Legend
                layout="vertical"
                align="right"
                verticalAlign="middle"
                iconType="circle"
                formatter={(value) => (
                  <span style={{ color: 'hsl(210, 40%, 98%)' }}>{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
