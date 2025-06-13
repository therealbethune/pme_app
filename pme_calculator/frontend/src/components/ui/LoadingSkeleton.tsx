import React from 'react';
import { Box, Skeleton } from '@mui/material';
import { tokens } from '../../styles/tokens';

interface LoadingSkeletonProps {
  variant?: 'card' | 'chart' | 'table' | 'metric' | 'upload';
  rows?: number;
  height?: number;
  animated?: boolean;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'card',
  rows = 3,
  height = 200,
  animated = true,
}) => {
  const getSkeletonContent = () => {
    switch (variant) {
      case 'chart':
        return (
          <Box sx={{ p: 3 }}>
            {/* Chart title */}
            <Skeleton
              variant="text"
              width="40%"
              height={24}
              animation={animated ? 'wave' : false}
              sx={{
                mb: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: tokens.borderRadius.base,
              }}
            />
            
            {/* Chart legend */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              {[1, 2, 3].map((i) => (
                <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Skeleton
                    variant="circular"
                    width={12}
                    height={12}
                    animation={animated ? 'wave' : false}
                    sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
                  />
                  <Skeleton
                    variant="text"
                    width={60}
                    height={16}
                    animation={animated ? 'wave' : false}
                    sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
                  />
                </Box>
              ))}
            </Box>
            
            {/* Chart area */}
            <Skeleton
              variant="rectangular"
              width="100%"
              height={height - 100}
              animation={animated ? 'wave' : false}
              sx={{
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: tokens.borderRadius.base,
              }}
            />
          </Box>
        );
      
      case 'table':
        return (
          <Box sx={{ p: 3 }}>
            {/* Table header */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              {[1, 2, 3, 4].map((i) => (
                <Skeleton
                  key={i}
                  variant="text"
                  width="25%"
                  height={20}
                  animation={animated ? 'wave' : false}
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.15)',
                    borderRadius: tokens.borderRadius.sm,
                  }}
                />
              ))}
            </Box>
            
            {/* Table rows */}
            {Array.from({ length: rows }).map((_, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 2, mb: 1 }}>
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton
                    key={i}
                    variant="text"
                    width="25%"
                    height={16}
                    animation={animated ? 'wave' : false}
                    sx={{
                      backgroundColor: 'rgba(255, 255, 255, 0.08)',
                      borderRadius: tokens.borderRadius.sm,
                    }}
                  />
                ))}
              </Box>
            ))}
          </Box>
        );
      
      case 'metric':
        return (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            {/* Metric value */}
            <Skeleton
              variant="text"
              width="60%"
              height={48}
              animation={animated ? 'wave' : false}
              sx={{
                margin: '0 auto',
                mb: 1,
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderRadius: tokens.borderRadius.base,
              }}
            />
            
            {/* Metric label */}
            <Skeleton
              variant="text"
              width="80%"
              height={20}
              animation={animated ? 'wave' : false}
              sx={{
                margin: '0 auto',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: tokens.borderRadius.sm,
              }}
            />
          </Box>
        );
      
      case 'upload':
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            {/* Upload icon placeholder */}
            <Skeleton
              variant="circular"
              width={64}
              height={64}
              animation={animated ? 'wave' : false}
              sx={{
                margin: '0 auto',
                mb: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }}
            />
            
            {/* Upload title */}
            <Skeleton
              variant="text"
              width="70%"
              height={24}
              animation={animated ? 'wave' : false}
              sx={{
                margin: '0 auto',
                mb: 1,
                backgroundColor: 'rgba(255, 255, 255, 0.12)',
                borderRadius: tokens.borderRadius.base,
              }}
            />
            
            {/* Upload description */}
            <Skeleton
              variant="text"
              width="90%"
              height={16}
              animation={animated ? 'wave' : false}
              sx={{
                margin: '0 auto',
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
                borderRadius: tokens.borderRadius.sm,
              }}
            />
          </Box>
        );
      
      default: // card
        return (
          <Box sx={{ p: 3 }}>
            {/* Card title */}
            <Skeleton
              variant="text"
              width="60%"
              height={24}
              animation={animated ? 'wave' : false}
              sx={{
                mb: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.12)',
                borderRadius: tokens.borderRadius.base,
              }}
            />
            
            {/* Content lines */}
            {Array.from({ length: rows }).map((_, index) => (
              <Skeleton
                key={index}
                variant="text"
                width={index === rows - 1 ? '40%' : '100%'}
                height={16}
                animation={animated ? 'wave' : false}
                sx={{
                  mb: 1,
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  borderRadius: tokens.borderRadius.sm,
                }}
              />
            ))}
            
            {/* Main content area */}
            <Skeleton
              variant="rectangular"
              width="100%"
              height={height - 120}
              animation={animated ? 'wave' : false}
              sx={{
                mt: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: tokens.borderRadius.base,
              }}
            />
          </Box>
        );
    }
  };

  return (
    <Box
      sx={{
        background: tokens.gradients.glassCard,
        backdropFilter: tokens.backdrop.blur.md,
        border: '1px solid rgba(255, 255, 255, 0.15)',
        borderRadius: tokens.borderRadius.lg,
        boxShadow: tokens.shadow.glass,
        overflow: 'hidden',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: '-100%',
          width: '100%',
          height: '100%',
          background: animated
            ? 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent)'
            : 'none',
          animation: animated ? 'shimmer 2s infinite' : 'none',
          '@keyframes shimmer': {
            '0%': { left: '-100%' },
            '100%': { left: '100%' },
          },
        },
      }}
    >
      {getSkeletonContent()}
    </Box>
  );
};

// Grid of skeletons for dashboard layouts
export const SkeletonGrid: React.FC<{
  count?: number;
  variant?: LoadingSkeletonProps['variant'];
  animated?: boolean;
}> = ({ count = 6, variant = 'card', animated = true }) => {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          lg: 'repeat(3, 1fr)',
        },
        gap: 3,
        p: 3,
      }}
    >
      {Array.from({ length: count }).map((_, index) => (
        <LoadingSkeleton
          key={index}
          variant={variant}
          animated={animated}
          height={variant === 'metric' ? 120 : 200}
        />
      ))}
    </Box>
  );
};

export default LoadingSkeleton; 