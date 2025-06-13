import React from 'react';
import { Box } from '@mui/material';
import { tokens } from '../../styles/tokens';
import { useColorMode } from '../../contexts/ColorModeContext';

interface GradientBackgroundProps {
  children: React.ReactNode;
  variant?: 'default' | 'dark' | 'financial' | 'minimal';
  className?: string;
}

export const GradientBackground: React.FC<GradientBackgroundProps> = ({
  children,
  variant = 'default',
  className = '',
}) => {
  const { isDarkMode } = useColorMode();

  const getBackgroundStyles = () => {
    const baseStyles = {
      minHeight: '100vh',
      position: 'relative' as const,
      overflow: 'hidden' as const,
    };

    switch (variant) {
      case 'financial':
        return {
          ...baseStyles,
          background: isDarkMode 
            ? `
              linear-gradient(135deg, #0f172a 0%, #1e293b 30%, #334155 60%, #475569 100%),
              radial-gradient(ellipse at 20% 80%, rgba(59, 130, 246, 0.2) 0%, transparent 60%),
              radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at 40% 40%, rgba(34, 197, 94, 0.12) 0%, transparent 60%),
              radial-gradient(ellipse at 90% 90%, rgba(245, 158, 11, 0.08) 0%, transparent 40%)
            `
            : `
              linear-gradient(135deg, #f8fafc 0%, #e2e8f0 20%, #cbd5e1 40%, #94a3b8 100%),
              radial-gradient(ellipse at 20% 80%, rgba(59, 130, 246, 0.12) 0%, transparent 60%),
              radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
              radial-gradient(ellipse at 40% 40%, rgba(34, 197, 94, 0.08) 0%, transparent 60%),
              radial-gradient(ellipse at 90% 90%, rgba(245, 158, 11, 0.06) 0%, transparent 40%)
            `,
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '40vh',
            background: isDarkMode
              ? 'linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.4) 50%, transparent 100%)'
              : 'linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, rgba(248, 250, 252, 0.5) 50%, transparent 100%)',
            zIndex: 1,
          },
        };

      case 'dark':
        return {
          ...baseStyles,
          background: `
            linear-gradient(135deg, #111827 0%, #1f2937 50%, #374151 100%),
            radial-gradient(circle at 30% 40%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 70% 70%, rgba(139, 92, 246, 0.1) 0%, transparent 50%)
          `,
        };

      case 'minimal':
        return {
          ...baseStyles,
          background: isDarkMode 
            ? tokens.colors.background.dark 
            : tokens.colors.background.light,
        };

      default:
        return {
          ...baseStyles,
          background: isDarkMode 
            ? tokens.gradients.background.dark 
            : tokens.gradients.background.light,
        };
    }
  };

  const getFloatingElements = () => {
    if (variant === 'minimal') return null;

    return (
      <>
        {/* Floating orbs */}
        <Box
          sx={{
            position: 'absolute',
            top: '8%',
            left: '15%',
            width: '400px',
            height: '400px',
            borderRadius: '50%',
            background: isDarkMode
              ? 'radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0.06) 40%, transparent 70%)'
              : 'radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0.04) 40%, transparent 70%)',
            animation: 'float 12s ease-in-out infinite',
            zIndex: 0,
          }}
        />
        
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            right: '10%',
            width: '320px',
            height: '320px',
            borderRadius: '50%',
            background: isDarkMode
              ? 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 40%, transparent 70%)'
              : 'radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, rgba(139, 92, 246, 0.03) 40%, transparent 70%)',
            animation: 'float 16s ease-in-out infinite reverse',
            zIndex: 0,
          }}
        />

        <Box
          sx={{
            position: 'absolute',
            top: '25%',
            right: '35%',
            width: '240px',
            height: '240px',
            borderRadius: '50%',
            background: isDarkMode
              ? 'radial-gradient(circle, rgba(34, 197, 94, 0.08) 0%, rgba(34, 197, 94, 0.04) 40%, transparent 70%)'
              : 'radial-gradient(circle, rgba(34, 197, 94, 0.05) 0%, rgba(34, 197, 94, 0.025) 40%, transparent 70%)',
            animation: 'float 20s ease-in-out infinite',
            zIndex: 0,
          }}
        />

        <Box
          sx={{
            position: 'absolute',
            bottom: '20%',
            left: '25%',
            width: '180px',
            height: '180px',
            borderRadius: '50%',
            background: isDarkMode
              ? 'radial-gradient(circle, rgba(245, 158, 11, 0.06) 0%, rgba(245, 158, 11, 0.03) 40%, transparent 70%)'
              : 'radial-gradient(circle, rgba(245, 158, 11, 0.04) 0%, rgba(245, 158, 11, 0.02) 40%, transparent 70%)',
            animation: 'float 14s ease-in-out infinite reverse',
            zIndex: 0,
          }}
        />

        {/* Grid pattern overlay */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: isDarkMode
              ? `radial-gradient(circle, rgba(255, 255, 255, 0.02) 1px, transparent 1px)`
              : `radial-gradient(circle, rgba(0, 0, 0, 0.02) 1px, transparent 1px)`,
            backgroundSize: '50px 50px',
            zIndex: 0,
          }}
        />

        {/* CSS keyframes for animations */}
        <style>
          {`
            @keyframes float {
              0%, 100% {
                transform: translateY(0px) translateX(0px) rotate(0deg) scale(1);
              }
              25% {
                transform: translateY(-15px) translateX(8px) rotate(2deg) scale(1.02);
              }
              50% {
                transform: translateY(-25px) translateX(-5px) rotate(-1deg) scale(1.05);
              }
              75% {
                transform: translateY(-10px) translateX(-8px) rotate(1.5deg) scale(1.03);
              }
            }
          `}
        </style>
      </>
    );
  };

  return (
    <Box
      className={className}
      sx={getBackgroundStyles()}
    >
      {getFloatingElements()}
      
      {/* Content container */}
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default GradientBackground; 