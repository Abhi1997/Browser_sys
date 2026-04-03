import React, { useState, useMemo } from 'react';
import { Globe, MoreHorizontal, Plus, Pencil, Trash2, CheckCircle, XCircle, Search, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { DataTable } from '@/components/shared/DataTable';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { WhitelistEntry, BlacklistEntry } from '@/lib/types';
import { cn } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';
import {
  useWhitelist,
  useBlacklist,
  useAddToWhitelist,
  useAddToBlacklist,
  useRemoveFromWhitelist,
  useRemoveFromBlacklist,
  useUpdateWhitelistEntry,
  useUpdateBlacklistEntry,
} from '@/hooks/useDashboardData';
import { useAuth } from '@/contexts/AuthContext';

interface ListTableProps {
  type: 'whitelist' | 'blacklist';
  readOnly?: boolean;
}

export function ListTable({ type, readOnly = false }: ListTableProps) {
  const isWhitelist = type === 'whitelist';
  const { user } = useAuth();
  const { data: whitelist, isLoading: whitelistLoading } = useWhitelist();
  const { data: blacklist, isLoading: blacklistLoading } = useBlacklist();
  const items = isWhitelist ? whitelist : blacklist;
  const isLoading = isWhitelist ? whitelistLoading : blacklistLoading;
  
  const addToWhitelist = useAddToWhitelist();
  const addToBlacklist = useAddToBlacklist();
  const removeFromWhitelist = useRemoveFromWhitelist();
  const removeFromBlacklist = useRemoveFromBlacklist();
  const updateWhitelistEntry = useUpdateWhitelistEntry();
  const updateBlacklistEntry = useUpdateBlacklistEntry();
  
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchColumn, setSearchColumn] = useState('all');
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  const handleSort = (key: string) => {
    setSortConfig(current => {
      if (current?.key === key) {
        if (current.direction === 'asc') return { key, direction: 'desc' };
        return null;
      }
      return { key, direction: 'asc' };
    });
  };

  const SortIcon = ({ columnKey }: { columnKey: string }) => {
    if (sortConfig?.key !== columnKey) return <ArrowUpDown className="ml-2 h-4 w-4 text-muted-foreground/50" />;
    return sortConfig.direction === 'asc' 
      ? <ArrowUp className="ml-2 h-4 w-4 text-primary" /> 
      : <ArrowDown className="ml-2 h-4 w-4 text-primary" />;
  };

  const processedItems = useMemo(() => {
    if (!items) return [];
    
    // Filter
    let result = items.filter((i: any) => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      const desc = i.description || i.reason || '';
      
      switch (searchColumn) {
        case 'url':
          return i.url.toLowerCase().includes(term);
        case 'description':
          return desc.toLowerCase().includes(term);
        case 'addedBy':
          return i.addedBy?.toString().toLowerCase().includes(term);
        case 'all':
        default:
          return (
            i.url.toLowerCase().includes(term) ||
            desc.toLowerCase().includes(term) ||
            i.addedBy?.toString().toLowerCase().includes(term)
          );
      }
    });

    // Sort
    if (sortConfig) {
      result = [...result].sort((a: any, b: any) => {
        let valA, valB;
        switch (sortConfig.key) {
          case 'url':
            valA = a.url.toLowerCase(); valB = b.url.toLowerCase(); break;
          case 'status':
            valA = a.isActive ? 1 : 0; valB = b.isActive ? 1 : 0; break;
          case 'addedBy':
            valA = a.addedBy; valB = b.addedBy; break;
          case 'addedAt':
            valA = new Date(a.addedAt).getTime();
            valB = new Date(b.addedAt).getTime();
            break;
          default:
            return 0;
        }
        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return result;
  }, [items, searchTerm, sortConfig]);

  const handleToggleStatus = (itemId: string) => {
    const item = items?.find((i: any) => i.id === itemId);
    if (!item) return;
    
    const updates = { isActive: !item.isActive };
    if (isWhitelist) {
      updateWhitelistEntry.mutate({ id: itemId, updates });
    } else {
      updateBlacklistEntry.mutate({ id: itemId, updates });
    }
  };

  const handleDelete = (itemId: string) => {
    if (isWhitelist) {
      removeFromWhitelist.mutate(itemId);
    } else {
      removeFromBlacklist.mutate(itemId);
    }
  };

  const handleAdd = () => {
    if (!newUrl.trim()) return;
    
    const entry: any = {
      domain: newUrl.trim(),
      url: newUrl.trim(),
      mode: 'free',
      addedBy: user?.id || '1',  // Use current user ID or default to admin
    };
    
    if (isWhitelist) {
      entry.description = newDescription.trim();
      addToWhitelist.mutate(entry);
    } else {
      entry.reason = newDescription.trim();
      addToBlacklist.mutate(entry);
    }
    
    setNewUrl('');
    setNewDescription('');
    setIsAddDialogOpen(false);
  };

  if (isLoading) {
    return (
      <div className="glass-card p-6">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  const columns = [
    {
      key: 'url',
      header: (
        <Button variant="ghost" onClick={() => handleSort('url')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          URL <SortIcon columnKey="url" />
        </Button>
      ),
      render: (item: WhitelistEntry | BlacklistEntry) => (
        <div className="flex items-center gap-3">
          <div className={cn(
            "h-10 w-10 rounded-lg flex items-center justify-center",
            isWhitelist ? "bg-success/10" : "bg-destructive/10"
          )}>
            <Globe className={cn(
              "h-5 w-5",
              isWhitelist ? "text-success" : "text-destructive"
            )} />
          </div>
          <div>
            <p className="font-medium text-foreground font-mono text-sm">{item.url}</p>
            <p className="text-xs text-muted-foreground">
              {'description' in item ? item.description : ('reason' in item ? item.reason : '')}
            </p>
          </div>
        </div>
      ),
    },
    {
      key: 'status',
      header: (
        <Button variant="ghost" onClick={() => handleSort('status')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Status <SortIcon columnKey="status" />
        </Button>
      ),
      render: (item: WhitelistEntry | BlacklistEntry) => (
        <Badge variant="outline" className={
          item.isActive 
            ? (isWhitelist 
                ? 'bg-success/20 text-success border-success/30' 
                : 'bg-destructive/20 text-destructive border-destructive/30')
            : 'bg-muted text-muted-foreground'
        }>
          {item.isActive ? 'Active' : 'Disabled'}
        </Badge>
      ),
    },
    {
      key: 'addedBy',
      header: (
        <Button variant="ghost" onClick={() => handleSort('addedBy')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Added By <SortIcon columnKey="addedBy" />
        </Button>
      ),
      render: (item: WhitelistEntry | BlacklistEntry) => (
        <span className="text-muted-foreground text-sm">{item.addedBy}</span>
      ),
    },
    {
      key: 'addedAt',
      header: (
        <Button variant="ghost" onClick={() => handleSort('addedAt')} className="-ml-4 hover:bg-transparent text-muted-foreground font-semibold">
          Added <SortIcon columnKey="addedAt" />
        </Button>
      ),
      render: (item: WhitelistEntry | BlacklistEntry) => (
        <span className="text-muted-foreground text-sm">
          {new Date(item.addedAt).toLocaleDateString()}
        </span>
      ),
    },
    ...(readOnly ? [] : [{
      key: 'actions',
      header: '',
      render: (item: WhitelistEntry | BlacklistEntry) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Pencil className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleToggleStatus(item.id)}>
              {item.isActive ? (
                <>
                  <XCircle className="mr-2 h-4 w-4" />
                  Disable
                </>
              ) : (
                <>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Enable
                </>
              )}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem 
              onClick={() => handleDelete(item.id)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Remove
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    }]),
  ];

  return (
    <>
      <div className="glass-card p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-lg font-semibold text-foreground capitalize">{type}</h3>
            <p className="text-sm text-muted-foreground">
              {isWhitelist ? 'Allowed URLs' : 'Blocked URLs'}
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <div className="flex shadow-sm rounded-md grow group">
              <Select value={searchColumn} onValueChange={setSearchColumn}>
                <SelectTrigger className="w-[130px] rounded-r-none border-r-0 focus:ring-0 focus:border-input bg-muted/50 transition-colors hover:bg-muted font-medium cursor-pointer">
                  <SelectValue placeholder="Filter by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Fields</SelectItem>
                  <SelectItem value="url">URL</SelectItem>
                  <SelectItem value="description">Description</SelectItem>
                  <SelectItem value="addedBy">Added By</SelectItem>
                </SelectContent>
              </Select>
              <div className="relative w-full sm:w-56 group-hover:border-primary/50 transition-colors">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
                <Input
                  placeholder="Search URLs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 rounded-l-none border-l-0 focus-visible:ring-1 focus-visible:ring-offset-0 focus-visible:border-primary transition-all"
                />
              </div>
            </div>
            {!readOnly && (
              <Button 
                onClick={() => setIsAddDialogOpen(true)}
                className={cn(
                  "gap-2 whitespace-nowrap hidden sm:flex",
                  isWhitelist 
                    ? "bg-success hover:bg-success/90 text-success-foreground" 
                    : "bg-destructive hover:bg-destructive/90"
                )}
              >
                <Plus className="h-4 w-4" />
                Add URL
              </Button>
            )}
          </div>
          {!readOnly && (
            <Button 
              onClick={() => setIsAddDialogOpen(true)}
              className={cn(
                "gap-2 whitespace-nowrap w-full sm:hidden mt-2",
                isWhitelist 
                  ? "bg-success hover:bg-success/90 text-success-foreground" 
                  : "bg-destructive hover:bg-destructive/90"
              )}
            >
              <Plus className="h-4 w-4" />
              Add URL
            </Button>
          )}
        </div>
        <DataTable
          data={processedItems}
          columns={columns as any}
          emptyMessage={`No URLs in ${type}`}
        />
      </div>

      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add to {isWhitelist ? 'Whitelist' : 'Blacklist'}</DialogTitle>
            <DialogDescription>
              {isWhitelist 
                ? 'Add a URL that students can access.'
                : 'Add a URL that should be blocked.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="url">URL</Label>
              <Input
                id="url"
                placeholder="example.com"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">
                {isWhitelist ? 'Description' : 'Reason'}
              </Label>
              <Input
                id="description"
                placeholder={isWhitelist ? 'Educational resource' : 'Social media distraction'}
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAdd} className={
              isWhitelist 
                ? "bg-success hover:bg-success/90 text-success-foreground" 
                : ""
            }>
              Add to {type}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
