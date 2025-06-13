// Design Tokens for PME Calculator
// Unified styling system for consistent UI/UX

export const tokens = {
  // Color Palette
  colors: {
    // Primary brand colors
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
    },
    
    // Semantic colors
    success: {
      50: '#f0fdf4',
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#14532d',
    },
    
    warning: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
    
    error: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
    
    // Neutral grays
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
    
    // Dark mode colors
    dark: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
      950: '#020617',
    },
    
    // Theme-aware colors
    background: {
      light: '#ffffff',
      dark: '#0a0a0a',
    },
    
    surface: {
      light: '#ffffff',
      dark: '#111111',
    },
    
    text: {
      primary: {
        light: '#111827',
        dark: '#f9fafb',
      },
      secondary: {
        light: '#6b7280',
        dark: '#9ca3af',
      },
      tertiary: {
        light: '#9ca3af',
        dark: '#6b7280',
      },
    },
    
    border: {
      light: '#e5e7eb',
      dark: '#262626',
    },
    
    // Chart colors for data visualization
    chart: [
      '#0ea5e9', // Primary blue
      '#22c55e', // Success green
      '#f59e0b', // Warning amber
      '#ef4444', // Error red
      '#8b5cf6', // Purple
      '#06b6d4', // Cyan
      '#84cc16', // Lime
      '#f97316', // Orange
      '#ec4899', // Pink
      '#10b981', // Emerald
    ],
    
    // Financial indicators
    financial: {
      positive: '#22c55e',
      negative: '#ef4444',
      neutral: '#6b7280',
      benchmark: '#8b5cf6',
    },
  },
  
  // Typography Scale
  typography: {
    // Font families
    fontFamily: {
      sans: ['Inter', 'SF Pro Display', 'Helvetica Neue', 'Arial', 'sans-serif'],
      mono: ['SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'monospace'],
    },
    
    // Font sizes (rem values)
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem',    // 48px
    },
    
    // Font weights
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
    },
    
    // Line heights
    lineHeight: {
      tight: '1.25',
      normal: '1.5',
      relaxed: '1.75',
    },
  },
  
  // Spacing Scale (rem values)
  spacing: {
    px: '1px',
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
    32: '8rem',     // 128px
  },
  
  // Border Radius
  borderRadius: {
    none: '0',
    sm: '0.25rem',   // 4px
    base: '0.5rem',  // 8px
    md: '0.75rem',   // 12px
    lg: '1rem',      // 16px - Primary radius
    xl: '1.5rem',    // 24px
    '2xl': '2rem',   // 32px
    full: '9999px',
  },
  
  // Shadows & Elevation
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    
    // Glassmorphism shadows
    glass: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
    glassHover: '0 8px 32px 0 rgba(31, 38, 135, 0.5)',
  },
  
  // Backdrop filters for glassmorphism
  backdrop: {
    blur: {
      sm: 'blur(4px)',
      base: 'blur(8px)',
      md: 'blur(12px)',
      lg: 'blur(16px)',
      xl: 'blur(24px)',
    },
  },
  
  // Gradients
  gradients: {
    // Primary gradient backgrounds
    primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    success: 'linear-gradient(135deg, #667eea 0%, #22c55e 100%)',
    warning: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    error: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)',
    
    // Light mode card backgrounds
    cardBg: {
      light: 'linear-gradient(145deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
      dark: 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
    },
    
    glassCard: {
      light: 'linear-gradient(145deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%)',
      dark: 'linear-gradient(145deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%)',
    },
    
    // Background gradients
    background: {
      light: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
      dark: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    },
    
    // Data visualization gradients
    performance: 'linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #22c55e 100%)',
    heatmap: 'linear-gradient(90deg, #3b82f6 0%, #06b6d4 25%, #22c55e 50%, #f59e0b 75%, #ef4444 100%)',
  },
  
  // Z-index scale
  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800,
  },
  
  // Breakpoints for responsive design
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  // Animation & Transitions
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      linear: 'linear',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
  
  // Component-specific styles
  components: {
    card: {
      light: {
        background: 'rgba(255, 255, 255, 0.08)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: '1rem',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      },
      dark: {
        background: 'rgba(255, 255, 255, 0.04)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '1rem',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
      },
    },
    
    button: {
      borderRadius: '0.75rem',
      fontWeight: '500',
      transition: 'all 150ms cubic-bezier(0.4, 0, 0.2, 1)',
    },
    
    input: {
      light: {
        borderRadius: '0.5rem',
        border: '1px solid rgba(209, 213, 219, 0.5)',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(8px)',
      },
      dark: {
        borderRadius: '0.5rem',
        border: '1px solid rgba(64, 64, 64, 0.5)',
        backgroundColor: 'rgba(255, 255, 255, 0.02)',
        backdropFilter: 'blur(8px)',
      },
    },
  },
} as const;

// Type definitions for TypeScript
export type TokenColors = typeof tokens.colors;
export type TokenSpacing = typeof tokens.spacing;
export type TokenTypography = typeof tokens.typography;

// Utility functions for accessing tokens
export const getColor = (color: string, shade?: number) => {
  const parts = color.split('.');
  let value: any = tokens.colors;
  
  for (const part of parts) {
    value = value?.[part];
  }
  
  if (shade && typeof value === 'object') {
    return value[shade];
  }
  
  return value;
};

export const getSpacing = (size: keyof typeof tokens.spacing) => tokens.spacing[size];

export const getFontSize = (size: keyof typeof tokens.typography.fontSize) => 
  tokens.typography.fontSize[size];

// Formatter functions for financial data
export const formatters = {
  currency: (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  },
  
  currencyDetailed: (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  },
  
  percentage: (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 2,
    }).format(value / 100);
  },
  
  multiple: (value: number): string => {
    return `${value.toFixed(2)}x`;
  },
  
  number: (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value);
  },
  
  compactNumber: (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(value);
  },
};

// Alias formatters for global use
export const fmtCurrency = formatters.currency;
export const fmtPct = formatters.percentage;
export const fmtMultiple = formatters.multiple;

// Theme-aware utility functions
export const getThemeAwareColor = (lightColor: string, darkColor: string, isDarkMode: boolean) => {
  return isDarkMode ? darkColor : lightColor;
};

export const getThemeAwareGradient = (gradientObj: { light: string; dark: string }, isDarkMode: boolean) => {
  return isDarkMode ? gradientObj.dark : gradientObj.light;
};

export const getThemeAwareComponent = (componentObj: { light: any; dark: any }, isDarkMode: boolean) => {
  return isDarkMode ? componentObj.dark : componentObj.light;
}; 