import React, { useState } from 'react';
import { Globe, MoreHorizontal, Plus, Pencil, Trash2, CheckCircle, XCircle } from 'lucide-react';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { mockWhitelist, mockBlacklist } from '@/lib/mock-data';
import { WhitelistEntry, BlacklistEntry } from '@/lib/types';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface ListTableProps {
  type: 'whitelist' | 'blacklist';
  readOnly?: boolean;
}

export function ListTable({ type, readOnly = false }: ListTableProps) {
  const [items, setItems] = useState(
    type === 'whitelist' ? mockWhitelist : mockBlacklist
  );
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newDescription, setNewDescription] = useState('');

  const isWhitelist = type === 'whitelist';

  const handleToggleStatus = (itemId: string) => {
    setItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, isActive: !item.isActive } : item
    ));
    toast({
      title: 'Entry updated',
      description: 'The entry status has been changed.',
    });
  };

  const handleDelete = (itemId: string) => {
    setItems(prev => prev.filter(item => item.id !== itemId));
    toast({
      title: 'Entry removed',
      description: `URL removed from ${type}.`,
      variant: 'destructive',
    });
  };

  const handleAdd = () => {
    if (!newUrl.trim()) return;
    
    const newItem = {
      id: Date.now().toString(),
      url: newUrl,
      [isWhitelist ? 'description' : 'reason']: newDescription,
      addedBy: 'admin',
      addedAt: new Date().toISOString(),
      isActive: true,
    };
    
    setItems(prev => [newItem as any, ...prev]);
    setNewUrl('');
    setNewDescription('');
    setIsAddDialogOpen(false);
    
    toast({
      title: 'Entry added',
      description: `URL added to ${type}.`,
    });
  };

  const columns = [
    {
      key: 'url',
      header: 'URL',
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
      header: 'Status',
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
      header: 'Added By',
      render: (item: WhitelistEntry | BlacklistEntry) => (
        <span className="text-muted-foreground text-sm">{item.addedBy}</span>
      ),
    },
    {
      key: 'addedAt',
      header: 'Added',
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
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-foreground capitalize">{type}</h3>
            <p className="text-sm text-muted-foreground">
              {isWhitelist ? 'Allowed URLs' : 'Blocked URLs'}
            </p>
          </div>
          {!readOnly && (
            <Button 
              onClick={() => setIsAddDialogOpen(true)}
              className={cn(
                "gap-2",
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
          data={items}
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
