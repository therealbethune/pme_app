import React, { createContext, useContext, useMemo, useState, useEffect } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { tokens } from '../styles/tokens';

type ColorMode = 'light' | 'dark';

interface ColorModeContextType {
  mode: ColorMode;
  toggleColorMode: () => void;
  isDarkMode: boolean;
}

const ColorModeContext = createContext<ColorModeContextType>({
  mode: 'light',
  toggleColorMode: () => {},
  isDarkMode: false,
});

export const useColorMode = () => useContext(ColorModeContext);

export const ColorModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize from localStorage or system preference
  const [mode, setMode] = useState<ColorMode>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('glassfunds-color-mode');
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }
      // Check system preference
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  });

  // Apply theme to HTML element and localStorage
  useEffect(() => {
    const root = document.documentElement;
    
    if (mode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    localStorage.setItem('glassfunds-color-mode', mode);
  }, [mode]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      // Only auto-switch if user hasn't manually set a preference
      if (!localStorage.getItem('glassfunds-color-mode')) {
        setMode(e.matches ? 'dark' : 'light');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  // Create enhanced MUI theme with design tokens
  const muiTheme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: tokens.colors.primary[600],
            light: tokens.colors.primary[400],
            dark: tokens.colors.primary[800],
          },
          secondary: {
            main: tokens.colors.primary[700],
            light: tokens.colors.primary[500],
            dark: tokens.colors.primary[900],
          },
          success: {
            main: tokens.colors.success[600],
            light: tokens.colors.success[400],
            dark: tokens.colors.success[800],
          },
          warning: {
            main: tokens.colors.warning[600],
            light: tokens.colors.warning[400],
            dark: tokens.colors.warning[800],
          },
          error: {
            main: tokens.colors.error[600],
            light: tokens.colors.error[400],
            dark: tokens.colors.error[800],
          },
          background: {
            default: mode === 'light' ? tokens.colors.background.light : tokens.colors.background.dark,
            paper: mode === 'light' ? tokens.colors.surface.light : tokens.colors.surface.dark,
          },
          text: {
            primary: mode === 'light' ? tokens.colors.text.primary.light : tokens.colors.text.primary.dark,
            secondary: mode === 'light' ? tokens.colors.text.secondary.light : tokens.colors.text.secondary.dark,
          },
          divider: mode === 'light' ? tokens.colors.border.light : tokens.colors.border.dark,
        },
        typography: {
          fontFamily: tokens.typography.fontFamily.sans.join(', '),
          h1: {
            fontSize: tokens.typography.fontSize['5xl'],
            fontWeight: tokens.typography.fontWeight.bold,
            lineHeight: tokens.typography.lineHeight.tight,
          },
          h2: {
            fontSize: tokens.typography.fontSize['4xl'],
            fontWeight: tokens.typography.fontWeight.bold,
            lineHeight: tokens.typography.lineHeight.tight,
          },
          h3: {
            fontSize: tokens.typography.fontSize['3xl'],
            fontWeight: tokens.typography.fontWeight.semibold,
            lineHeight: tokens.typography.lineHeight.tight,
          },
          h4: {
            fontSize: tokens.typography.fontSize['2xl'],
            fontWeight: tokens.typography.fontWeight.semibold,
            lineHeight: tokens.typography.lineHeight.normal,
          },
          h5: {
            fontSize: tokens.typography.fontSize.xl,
            fontWeight: tokens.typography.fontWeight.medium,
            lineHeight: tokens.typography.lineHeight.normal,
          },
          h6: {
            fontSize: tokens.typography.fontSize.lg,
            fontWeight: tokens.typography.fontWeight.medium,
            lineHeight: tokens.typography.lineHeight.normal,
          },
          body1: {
            fontSize: tokens.typography.fontSize.base,
            lineHeight: tokens.typography.lineHeight.relaxed,
          },
          body2: {
            fontSize: tokens.typography.fontSize.sm,
            lineHeight: tokens.typography.lineHeight.normal,
          },
        },
        shape: {
          borderRadius: parseInt(tokens.borderRadius.lg.replace('rem', '')) * 16, // Convert rem to px
        },
        components: {
          MuiCssBaseline: {
            styleOverrides: {
              body: {
                backgroundImage: mode === 'light' 
                  ? tokens.gradients.background.light 
                  : tokens.gradients.background.dark,
                minHeight: '100vh',
              },
              '*': {
                scrollbarWidth: 'thin',
                scrollbarColor: mode === 'light' ? '#cbd5e1 #f1f5f9' : '#475569 #1e293b',
              },
              '*::-webkit-scrollbar': {
                width: '8px',
              },
              '*::-webkit-scrollbar-track': {
                background: mode === 'light' ? '#f1f5f9' : '#1e293b',
              },
              '*::-webkit-scrollbar-thumb': {
                backgroundColor: mode === 'light' ? '#cbd5e1' : '#475569',
                borderRadius: '4px',
                '&:hover': {
                  backgroundColor: mode === 'light' ? '#94a3b8' : '#64748b',
                },
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
                border: `1px solid ${mode === 'light' ? tokens.colors.border.light : tokens.colors.border.dark}`,
                backdropFilter: tokens.backdrop.blur.md,
                backgroundColor: mode === 'light' 
                  ? 'rgba(255, 255, 255, 0.8)' 
                  : 'rgba(17, 17, 17, 0.8)',
              },
            },
          },
          MuiButton: {
            styleOverrides: {
              root: {
                borderRadius: tokens.borderRadius.md,
                fontWeight: tokens.typography.fontWeight.medium,
                textTransform: 'none',
                transition: `all ${tokens.animation.duration.normal} ${tokens.animation.easing.inOut}`,
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: tokens.borderRadius.lg,
                boxShadow: mode === 'light' ? tokens.shadow.base : tokens.shadow.lg,
                backdropFilter: tokens.backdrop.blur.md,
                backgroundColor: mode === 'light' 
                  ? 'rgba(255, 255, 255, 0.8)' 
                  : 'rgba(17, 17, 17, 0.8)',
                border: `1px solid ${mode === 'light' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'}`,
              },
            },
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                backdropFilter: tokens.backdrop.blur.md,
                backgroundColor: mode === 'light' 
                  ? 'rgba(255, 255, 255, 0.8)' 
                  : 'rgba(17, 17, 17, 0.8)',
                borderBottom: `1px solid ${mode === 'light' ? tokens.colors.border.light : tokens.colors.border.dark}`,
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                '& .MuiOutlinedInput-root': {
                  borderRadius: tokens.borderRadius.md,
                  backdropFilter: tokens.backdrop.blur.base,
                  backgroundColor: mode === 'light' 
                    ? 'rgba(255, 255, 255, 0.05)' 
                    : 'rgba(255, 255, 255, 0.02)',
                },
              },
            },
          },
        },
      }),
    [mode]
  );

  const contextValue = useMemo(
    () => ({
      mode,
      toggleColorMode,
      isDarkMode: mode === 'dark',
    }),
    [mode]
  );

  return (
    <ColorModeContext.Provider value={contextValue}>
      <MuiThemeProvider theme={muiTheme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ColorModeContext.Provider>
  );
}; 