import React, { createContext, useContext, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark' | 'system';
export type Contrast = 'normal' | 'high';
export type Magnifier = '1x' | '1.1x' | '1.2x';

interface SettingsContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  contrast: Contrast;
  setContrast: (contrast: Contrast) => void;
  magnifier: Magnifier;
  setMagnifier: (magnifier: Magnifier) => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(
    () => (localStorage.getItem('ui-theme') as Theme) || 'light'
  );
  const [contrast, setContrastState] = useState<Contrast>(
    () => (localStorage.getItem('ui-contrast') as Contrast) || 'normal'
  );
  const [magnifier, setMagnifierState] = useState<Magnifier>(
    () => (localStorage.getItem('ui-magnifier') as Magnifier) || '1x'
  );

  const setTheme = (newTheme: Theme) => {
    localStorage.setItem('ui-theme', newTheme);
    setThemeState(newTheme);
  };

  const setContrast = (newContrast: Contrast) => {
    localStorage.setItem('ui-contrast', newContrast);
    setContrastState(newContrast);
  };

  const setMagnifier = (newMagnifier: Magnifier) => {
    localStorage.setItem('ui-magnifier', newMagnifier);
    setMagnifierState(newMagnifier);
  };

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark', 'high-contrast');

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }

    if (contrast === 'high') {
      root.classList.add('high-contrast');
    }
  }, [theme, contrast]);

  useEffect(() => {
    const html = document.documentElement;
    if (magnifier === '1.1x') {
      html.style.fontSize = '110%';
    } else if (magnifier === '1.2x') {
      html.style.fontSize = '120%';
    } else {
      html.style.fontSize = '100%';
    }
  }, [magnifier]);

  return (
    <SettingsContext.Provider value={{ theme, setTheme, contrast, setContrast, magnifier, setMagnifier }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
}
