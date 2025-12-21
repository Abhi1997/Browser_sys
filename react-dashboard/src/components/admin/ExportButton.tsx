import React, { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { toast } from '@/hooks/use-toast';

interface ExportButtonProps {
  disabled?: boolean;
}

export function ExportButton({ disabled = false }: ExportButtonProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportOptions, setExportOptions] = useState({
    users: true,
    whitelist: true,
    blacklist: true,
    logs: false,
  });

  const handleExport = async () => {
    setIsExporting(true);
    
    // Simulate export process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create mock download
    const exportData = {
      exportedAt: new Date().toISOString(),
      options: exportOptions,
      message: 'Database export completed successfully',
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `database-export-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setIsExporting(false);
    setIsDialogOpen(false);
    
    toast({
      title: 'Export complete',
      description: 'Database snapshot has been downloaded.',
    });
  };

  if (disabled) {
    return (
      <Button variant="outline" disabled className="gap-2">
        <Download className="h-4 w-4" />
        Export Database
      </Button>
    );
  }

  return (
    <>
      <Button 
        variant="outline" 
        onClick={() => setIsDialogOpen(true)}
        className="gap-2"
      >
        <Download className="h-4 w-4" />
        Export Database
      </Button>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Export Database</DialogTitle>
            <DialogDescription>
              Select which data to include in the export. This action will be logged for security purposes.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="flex items-center space-x-3">
              <Checkbox
                id="users"
                checked={exportOptions.users}
                onCheckedChange={(checked) => 
                  setExportOptions(prev => ({ ...prev, users: checked === true }))
                }
              />
              <Label htmlFor="users" className="font-normal">
                Users table
              </Label>
            </div>
            <div className="flex items-center space-x-3">
              <Checkbox
                id="whitelist"
                checked={exportOptions.whitelist}
                onCheckedChange={(checked) => 
                  setExportOptions(prev => ({ ...prev, whitelist: checked === true }))
                }
              />
              <Label htmlFor="whitelist" className="font-normal">
                Whitelist entries
              </Label>
            </div>
            <div className="flex items-center space-x-3">
              <Checkbox
                id="blacklist"
                checked={exportOptions.blacklist}
                onCheckedChange={(checked) => 
                  setExportOptions(prev => ({ ...prev, blacklist: checked === true }))
                }
              />
              <Label htmlFor="blacklist" className="font-normal">
                Blacklist entries
              </Label>
            </div>
            <div className="flex items-center space-x-3">
              <Checkbox
                id="logs"
                checked={exportOptions.logs}
                onCheckedChange={(checked) => 
                  setExportOptions(prev => ({ ...prev, logs: checked === true }))
                }
              />
              <Label htmlFor="logs" className="font-normal">
                Activity logs (last 30 days)
              </Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)} disabled={isExporting}>
              Cancel
            </Button>
            <Button onClick={handleExport} disabled={isExporting} className="gap-2">
              {isExporting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  Download Export
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
