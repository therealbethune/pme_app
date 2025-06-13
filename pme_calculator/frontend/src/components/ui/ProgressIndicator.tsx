import React from 'react';
import { Box, LinearProgress, Typography, Portal } from '@mui/material';
import { tokens } from '../../styles/tokens';

interface ProgressIndicatorProps {
  visible: boolean;
  message?: string;
  progress?: number; // 0-100
  variant?: 'determinate' | 'indeterminate';
  color?: 'primary' | 'success' | 'warning' | 'error';
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  visible,
  message = 'Processing...',
  progress = 0,
  variant = 'indeterminate',
  color = 'primary',
}) => {
  if (!visible) return null;

  const getColorStyles = () => {
    switch (color) {
      case 'success':
        return {
          background: tokens.colors.success[500],
          glow: tokens.colors.success[400],
        };
      case 'warning':
        return {
          background: tokens.colors.warning[500],
          glow: tokens.colors.warning[400],
        };
      case 'error':
        return {
          background: tokens.colors.error[500],
          glow: tokens.colors.error[400],
        };
      default:
        return {
          background: tokens.colors.primary[500],
          glow: tokens.colors.primary[400],
        };
    }
  };

  const colorStyles = getColorStyles();

  return (
    <Portal>
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: tokens.zIndex.toast,
          background: tokens.gradients.glassCard,
          backdropFilter: tokens.backdrop.blur.md,
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: tokens.shadow.lg,
        }}
      >
        <Box
          sx={{
            maxWidth: '1200px',
            margin: '0 auto',
            px: 3,
            py: 2,
            display: 'flex',
            alignItems: 'center',
            gap: 2,
          }}
        >
          {/* Progress indicator */}
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Typography
                variant="body2"
                sx={{
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontWeight: tokens.typography.fontWeight.medium,
                  fontSize: tokens.typography.fontSize.sm,
                }}
              >
                {message}
              </Typography>
              
              {variant === 'determinate' && (
                <Typography
                  variant="caption"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.7)',
                    fontSize: tokens.typography.fontSize.xs,
                    fontFamily: tokens.typography.fontFamily.mono.join(', '),
                  }}
                >
                  {Math.round(progress)}%
                </Typography>
              )}
            </Box>
            
            <LinearProgress
              variant={variant}
              value={progress}
              sx={{
                height: 4,
                borderRadius: tokens.borderRadius.full,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: tokens.borderRadius.full,
                  background: `linear-gradient(90deg, ${colorStyles.background} 0%, ${colorStyles.glow} 100%)`,
                  boxShadow: `0 0 12px ${colorStyles.glow}40`,
                  animation: variant === 'indeterminate' 
                    ? 'glow 2s ease-in-out infinite alternate' 
                    : 'none',
                  '@keyframes glow': {
                    '0%': {
                      boxShadow: `0 0 8px ${colorStyles.glow}40`,
                    },
                    '100%': {
                      boxShadow: `0 0 16px ${colorStyles.glow}60`,
                    },
                  },
                },
              }}
            />
          </Box>
          
          {/* Animated dots */}
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {[0, 1, 2].map((i) => (
              <Box
                key={i}
                sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
                  '@keyframes pulse': {
                    '0%, 80%, 100%': {
                      opacity: 0.3,
                      transform: 'scale(0.8)',
                    },
                    '40%': {
                      opacity: 1,
                      transform: 'scale(1)',
                    },
                  },
                }}
              />
            ))}
          </Box>
        </Box>
      </Box>
    </Portal>
  );
};

// Hook for managing global progress state
export const useProgress = () => {
  const [state, setState] = React.useState({
    visible: false,
    message: 'Processing...',
    progress: 0,
    variant: 'indeterminate' as 'determinate' | 'indeterminate',
    color: 'primary' as 'primary' | 'success' | 'warning' | 'error',
  });

  const showProgress = React.useCallback((config: Partial<typeof state>) => {
    setState(prev => ({
      ...prev,
      visible: true,
      ...config,
    }));
  }, []);

  const hideProgress = React.useCallback(() => {
    setState(prev => ({ ...prev, visible: false }));
  }, []);

  const updateProgress = React.useCallback((progress: number, message?: string) => {
    setState(prev => ({
      ...prev,
      progress,
      ...(message && { message }),
      variant: 'determinate',
    }));
  }, []);

  return {
    ...state,
    showProgress,
    hideProgress,
    updateProgress,
  };
};

export default ProgressIndicator; 