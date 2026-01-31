import React, { useState } from 'react';
import { ChevronDown, ChevronRight, User, Globe, Folder, BookOpen, AlertCircle, Clock, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useActivity, useViolations, useStudentHistory, useUpdateStudentMode, useTeachers, useAssignStudentToTeacher } from '@/hooks/useDashboardData';
import { useAuth } from '@/contexts/AuthContext';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

const MODE_COLORS: Record<string, string> = {
  cached: 'bg-violet-500/20 text-violet-700 border-violet-500/30',
  study: 'bg-primary/20 text-primary border-primary/30',
  restricted: 'bg-warning/20 text-warning border-warning/30',
  free: 'bg-success/20 text-success border-success/30',
};

const MODE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  cached: Folder,
  study: BookOpen,
  restricted: AlertCircle,
  free: Globe,
};

interface StudentDetailCardProps {
  student: {
    id?: string;
    student_id?: string;
    user_id?: string;
    username?: string;
    gmail?: string;
    email?: string;
    mode?: string;
    assigned_mode?: string;
    is_active?: boolean;
    teacher_id?: string | number;
    teacherName?: string;
  };
}

export function StudentDetailCard({ student }: StudentDetailCardProps) {
  const [expanded, setExpanded] = useState(false);
  const { user } = useAuth();
  const studentId = String(student.student_id ?? student.id ?? '');
  const mode = student.mode ?? student.assigned_mode ?? 'restricted';
  const displayName = student.username ?? student.gmail ?? student.email ?? studentId;

  const { data: activity, isLoading: activityLoading } = useActivity(studentId, 50);
  const { data: violations, isLoading: violationsLoading } = useViolations(studentId, 50);
  const { data: browsingHistory, isLoading: historyLoading } = useStudentHistory(studentId, 50);
  const { data: teachers } = useTeachers();
  const updateMode = useUpdateStudentMode();
  const assignTeacher = useAssignStudentToTeacher();
  
  const isAdmin = user?.role === 'admin';
  const currentTeacherId = String(student.teacher_id ?? '');

  const handleModeChange = (newMode: string) => {
    if (user?.id && studentId) {
      updateMode.mutate({
        studentId,
        mode: newMode,
        changedBy: parseInt(user.id),
      });
    }
  };
  
  const handleTeacherChange = (teacherId: string) => {
    if (studentId) {
      assignTeacher.mutate({
        studentId,
        teacherId: teacherId === 'unassigned' ? null : teacherId,
      });
    }
  };

  const ModeIcon = MODE_ICONS[mode] ?? AlertCircle;

  return (
    <Card className="overflow-hidden">
      <CardHeader
        className="cursor-pointer py-4 hover:bg-muted/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {expanded ? (
              <ChevronDown className="h-5 w-5 text-muted-foreground shrink-0" />
            ) : (
              <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
            )}
            <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center shrink-0">
              <User className="h-5 w-5 text-muted-foreground" />
            </div>
            <div>
              <p className="font-medium text-foreground">{displayName}</p>
              <p className="text-xs text-muted-foreground">{student.gmail ?? student.email ?? studentId}</p>
            </div>
            <Badge variant="outline" className={cn('shrink-0', MODE_COLORS[mode] ?? '')}>
              <ModeIcon className="h-3 w-3 mr-1" />
              {mode?.toUpperCase() ?? 'N/A'}
            </Badge>
            {student.teacherName && (
              <Badge variant="secondary" className="shrink-0">
                Teacher: {student.teacherName}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2 shrink-0 flex-wrap" onClick={(e) => e.stopPropagation()}>
            {/* Admin can assign teacher */}
            {isAdmin && teachers && teachers.length > 0 && (
              <>
                <span className="text-sm text-muted-foreground">Teacher:</span>
                <Select
                  value={currentTeacherId || 'unassigned'}
                  onValueChange={handleTeacherChange}
                  disabled={assignTeacher.isPending}
                >
                  <SelectTrigger className="w-[130px] h-9">
                    <SelectValue placeholder="Assign..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="unassigned">Unassigned</SelectItem>
                    {(teachers as any[]).map((t: any) => (
                      <SelectItem key={t.id} value={String(t.id)}>
                        {t.username}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </>
            )}
            <span className="text-sm text-muted-foreground">Mode:</span>
            <Select
              value={mode}
              onValueChange={handleModeChange}
              disabled={updateMode.isPending || !user?.id}
            >
              <SelectTrigger className="w-[130px] h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="restricted">Restricted</SelectItem>
                <SelectItem value="study">Study</SelectItem>
                <SelectItem value="cached">Cached</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      {expanded && (
        <CardContent className="pt-0 border-t bg-muted/20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 py-4">
            {/* Violations */}
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-warning" />
                Violations ({violations?.length ?? 0})
              </h4>
              <div className="rounded-lg border bg-card p-3 max-h-48 overflow-y-auto">
                {violationsLoading ? (
                  <Skeleton className="h-20 w-full" />
                ) : !violations?.length ? (
                  <p className="text-sm text-muted-foreground">No violations</p>
                ) : (
                  <ul className="space-y-2 text-sm">
                    {(violations as any[]).map((v: any) => (
                      <li key={v.id} className="flex items-start gap-2 border-b border-border/50 pb-2 last:border-0">
                        <Clock className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium truncate">{v.url ?? v.attempted_url ?? '—'}</p>
                          <p className="text-xs text-muted-foreground">
                            {v.timestamp ?? v.createdAt ?? ''} · {v.reason ?? v.description ?? v.violation_type ?? ''}
                          </p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            {/* Browsing history (per-student) */}
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                Browsing history ({browsingHistory?.length ?? 0})
              </h4>
              <div className="rounded-lg border bg-card p-3 max-h-48 overflow-y-auto">
                {historyLoading ? (
                  <Skeleton className="h-20 w-full" />
                ) : !browsingHistory?.length ? (
                  <p className="text-sm text-muted-foreground">No browsing history yet</p>
                ) : (
                  <ul className="space-y-2 text-sm">
                    {(browsingHistory as any[]).map((h: any) => (
                      <li key={h.id} className="flex items-start gap-2 border-b border-border/50 pb-2 last:border-0">
                        <ExternalLink className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                        <div className="min-w-0">
                          <p className="font-medium truncate">{h.pageTitle || h.url || '—'}</p>
                          <p className="text-xs text-muted-foreground truncate">{h.url}</p>
                          <p className="text-xs text-muted-foreground">{h.visitedAt ? new Date(h.visitedAt).toLocaleString() : ''}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
