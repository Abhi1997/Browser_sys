import React, { useMemo } from 'react';
import { GraduationCap, Users, TrendingUp, BookOpen } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { useStudents, useActivity } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export function ClassStatsCards() {
  const { data: students, isLoading: studentsLoading } = useStudents();
  const { data: activities } = useActivity(undefined, 500);

  const classData = useMemo(() => {
    if (!students || students.length === 0) {
      return [];
    }

    // Group students by mode (as a proxy for "class")
    const modeGroups = ['cached', 'study', 'restricted', 'free', 'exam'];
    
    return modeGroups.map(mode => {
      const modeStudents = students.filter((s: any) => s.assignedMode === mode);
      const modeActivities = activities?.filter((a: any) => 
        modeStudents.some((s: any) => s.studentId === a.studentId)
      ) || [];

      // Calculate average activity (percentage of students with recent activity)
      const recentActivityThreshold = new Date();
      recentActivityThreshold.setHours(recentActivityThreshold.getHours() - 24);
      const activeStudents = new Set(
        modeActivities
          .filter((a: any) => new Date(a.visitStart || a.createdAt) >= recentActivityThreshold)
          .map((a: any) => a.studentId)
      ).size;
      
      const averageActivity = modeStudents.length > 0
        ? Math.round((activeStudents / modeStudents.length) * 100)
        : 0;

      return {
        classId: mode,
        className: `${mode.charAt(0).toUpperCase() + mode.slice(1)} Mode`,
        studentCount: modeStudents.length,
        averageActivity,
        completedLessons: 0, // Not tracked in current schema
        totalLessons: 0, // Not tracked in current schema
      };
    }).filter(c => c.studentCount > 0);
  }, [students, activities]);

  if (studentsLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    );
  }

  if (classData.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>No class data available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {classData.map((classItem, index) => {
        const completionRate = classItem.totalLessons > 0 
          ? Math.round((classItem.completedLessons / classItem.totalLessons) * 100)
          : 0;
        
        return (
          <div 
            key={classItem.classId}
            className="glass-card-hover p-6 animate-slide-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="h-12 w-12 rounded-xl gradient-teacher flex items-center justify-center">
                <GraduationCap className="h-6 w-6 text-success-foreground" />
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-foreground">{classItem.studentCount}</p>
                <p className="text-xs text-muted-foreground">students</p>
              </div>
            </div>
            
            <h3 className="font-semibold text-foreground mb-4">{classItem.className}</h3>
            
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Users className="h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Activity</span>
                    <span className="font-medium text-foreground">{classItem.averageActivity}%</span>
                  </div>
                  <Progress value={classItem.averageActivity} className="h-1.5" />
                </div>
              </div>
              
              <div className={cn(
                "flex items-center gap-2 text-sm pt-2 border-t border-border/50",
                classItem.averageActivity >= 75 ? "text-success" : 
                classItem.averageActivity >= 50 ? "text-warning" : "text-destructive"
              )}>
                <TrendingUp className="h-4 w-4" />
                <span>
                  {classItem.averageActivity >= 75 ? 'High engagement' :
                   classItem.averageActivity >= 50 ? 'Moderate engagement' : 'Low engagement'}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
