import React from 'react';
import { useSettings, Theme, Contrast, Magnifier } from '@/contexts/SettingsContext';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from '@/components/ui/dropdown-menu';
import { Monitor, Moon, Sun, Accessibility, ZoomIn, Contrast as ContrastIcon } from 'lucide-react';

export function SettingsMenu() {
  const { theme, setTheme, contrast, setContrast, magnifier, setMagnifier } = useSettings();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative group">
          <Accessibility className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
          <span className="sr-only">Accessibility & Theme Settings</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        
        <DropdownMenuLabel className="flex items-center gap-2">
          <Sun className="h-4 w-4" /> Theme
        </DropdownMenuLabel>
        <DropdownMenuRadioGroup value={theme} onValueChange={(v) => setTheme(v as Theme)}>
          <DropdownMenuRadioItem value="light">Light</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="dark">Dark</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="system">System Default</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>

        <DropdownMenuSeparator />

        <DropdownMenuLabel className="flex items-center gap-2">
          <ContrastIcon className="h-4 w-4" /> Contrast
        </DropdownMenuLabel>
        <DropdownMenuRadioGroup value={contrast} onValueChange={(v) => setContrast(v as Contrast)}>
          <DropdownMenuRadioItem value="normal">Normal</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="high">High Contrast</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>

        <DropdownMenuSeparator />

        <DropdownMenuLabel className="flex items-center gap-2">
          <ZoomIn className="h-4 w-4" /> Text Size
        </DropdownMenuLabel>
        <DropdownMenuRadioGroup value={magnifier} onValueChange={(v) => setMagnifier(v as Magnifier)}>
          <DropdownMenuRadioItem value="1x">Normal (100%)</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="1.1x">Large (110%)</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="1.2x">Extra Large (120%)</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>

      </DropdownMenuContent>
    </DropdownMenu>
  );
}
