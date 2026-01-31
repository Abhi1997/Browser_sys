import React from 'react';
import { Folder, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useCachedSites, useDeleteCachedSite } from '@/hooks/useDashboardData';
import { formatDistanceToNow } from 'date-fns';

export function CachedSitesTable() {
  const { data: sites, isLoading } = useCachedSites();
  const deleteCachedSite = useDeleteCachedSite();
  const [deletingId, setDeletingId] = React.useState<string | null>(null);

  const handleDelete = (id: string) => {
    setDeletingId(id);
    deleteCachedSite.mutate(id, {
      onSettled: () => setDeletingId(null),
    });
  };

  if (isLoading) {
    return <Skeleton className="h-64 w-full rounded-lg" />;
  }

  const list = sites ?? [];

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <div className="p-4 border-b bg-muted/30 flex items-center gap-2">
        <Folder className="h-4 w-4 text-violet-600" />
        <h3 className="font-semibold">Cached sites (offline)</h3>
        <Badge variant="secondary" className="ml-2">
          {list.length} site{list.length !== 1 ? 's' : ''}
        </Badge>
      </div>
      <p className="text-sm text-muted-foreground px-4 pt-2">
        Sites cached from the EduBrowser app (teachers/admins use &quot;Cache this page&quot;). Students in Cached mode can only view these. Remove entries here; the cached file remains on the device where it was saved.
      </p>
      {list.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground text-sm">
          No cached sites. Use &quot;Cache this page&quot; in the EduBrowser app to add offline pages.
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title / URL</TableHead>
              <TableHead>Added by</TableHead>
              <TableHead>Added</TableHead>
              <TableHead className="w-[80px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {list.map((site: any) => (
              <TableRow key={site.id}>
                <TableCell>
                  <div className="flex flex-col gap-0.5">
                    <span className="font-medium truncate max-w-[320px]" title={site.title || site.url}>
                      {site.title || site.url || '—'}
                    </span>
                    <span className="text-xs text-muted-foreground truncate max-w-[320px]" title={site.url}>
                      {site.url}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {site.addedByName ?? site.addedBy ?? '—'}
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {site.createdAt
                    ? formatDistanceToNow(new Date(site.createdAt), { addSuffix: true })
                    : '—'}
                </TableCell>
                <TableCell>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-destructive hover:text-destructive"
                        disabled={deletingId === String(site.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Remove cached site?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will remove the entry from the list. Students in Cached mode will no longer see it. The file may still exist on the device where it was cached.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={() => handleDelete(String(site.id))}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Remove
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
