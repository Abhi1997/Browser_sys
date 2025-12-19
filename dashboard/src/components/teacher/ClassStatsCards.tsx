import React from 'react';
import { GraduationCap, Users, TrendingUp, BookOpen } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { mockClassMetrics } from '@/lib/mock-data';
import { cn } from '@/lib/utils';

interface ClassStatsCardsProps {
  data?: typeof mockClassMetrics;
}

export function ClassStatsCards({ data = mockClassMetrics }: ClassStatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.map((classData, index) => {
        const completionRate = Math.round((classData.completedLessons / classData.totalLessons) * 100);
        
        return (
          <div 
            key={classData.classId}
            className="glass-card-hover p-6 animate-slide-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="h-12 w-12 rounded-xl gradient-teacher flex items-center justify-center">
                <GraduationCap className="h-6 w-6 text-success-foreground" />
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-foreground">{classData.studentCount}</p>
                <p className="text-xs text-muted-foreground">students</p>
              </div>
            </div>
            
            <h3 className="font-semibold text-foreground mb-4">{classData.className}</h3>
            
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Users className="h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Activity</span>
                    <span className="font-medium text-foreground">{classData.averageActivity}%</span>
                  </div>
                  <Progress value={classData.averageActivity} className="h-1.5" />
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <BookOpen className="h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium text-foreground">
                      {classData.completedLessons}/{classData.totalLessons}
                    </span>
                  </div>
                  <Progress value={completionRate} className="h-1.5" />
                </div>
              </div>
              
              <div className={cn(
                "flex items-center gap-2 text-sm pt-2 border-t border-border/50",
                classData.averageActivity >= 75 ? "text-success" : 
                classData.averageActivity >= 50 ? "text-warning" : "text-destructive"
              )}>
                <TrendingUp className="h-4 w-4" />
                <span>
                  {classData.averageActivity >= 75 ? 'High engagement' :
                   classData.averageActivity >= 50 ? 'Moderate engagement' : 'Low engagement'}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
