import { createTheme, ThemeOptions } from '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Palette {
    glass: {
      primary: string;
      secondary: string;
      accent: string;
      background: string;
    };
  }

  interface PaletteOptions {
    glass?: {
      primary?: string;
      secondary?: string;
      accent?: string;
      background?: string;
    };
  }
}

const baseTheme: ThemeOptions = {
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
};

export const lightTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'light',
    primary: {
      main: '#003d6d',
      light: '#1976d2',
      dark: '#002447',
    },
    secondary: {
      main: '#00d2c3',
      light: '#4dd0e1',
      dark: '#00acc1',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
    glass: {
      primary: '#003d6d',
      secondary: '#00d2c3',
      accent: '#1976d2',
      background: 'rgba(255, 255, 255, 0.9)',
    },
  },
});

export const darkTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'dark',
    primary: {
      main: '#4dd0e1',
      light: '#81e6f0',
      dark: '#00acc1',
    },
    secondary: {
      main: '#003d6d',
      light: '#1976d2',
      dark: '#002447',
    },
    background: {
      default: '#000000',
      paper: '#0a0a0a',
    },
    glass: {
      primary: '#4dd0e1',
      secondary: '#003d6d',
      accent: '#1976d2',
      background: 'rgba(10, 10, 10, 0.9)',
    },
  },
});

export const theme = lightTheme; // Default export
export default theme; 