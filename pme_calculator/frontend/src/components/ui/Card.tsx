import React, { ReactNode, useState } from 'react';
import {
  Card as MuiCard,
  CardContent,
  CardActions,
  CardHeader,
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Box,
  Collapse,
  Divider,
  CircularProgress,
  Alert,
  useTheme,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  MoreVert as MoreVertIcon,
  Error as ErrorIcon,
  ExpandLess,
  ExpandMore,
  Visibility,
  VisibilityOff,
  Fullscreen,
} from '@mui/icons-material';
import { tokens } from '../../styles/tokens';
import { useColorMode } from '../../contexts/ColorModeContext';

export interface CardProps {
  title?: string;
  icon?: ReactNode;
  children: ReactNode;
  variant?: 'default' | 'glass' | 'elevated' | 'minimal';
  collapsible?: boolean;
  defaultExpanded?: boolean;
  menuItems?: Array<{
    label: string;
    icon?: ReactNode;
    onClick: () => void;
    disabled?: boolean;
  }>;
  className?: string;
  fullWidth?: boolean;
  loading?: boolean;
  error?: string;
  onHide?: () => void;
  onFullscreen?: () => void;
  sx?: any;
}

export const Card: React.FC<CardProps> = ({
  title,
  icon,
  children,
  variant = 'default',
  collapsible = false,
  defaultExpanded = true,
  menuItems,
  className = '',
  fullWidth = true,
  loading = false,
  error,
  onHide,
  onFullscreen,
  sx = {},
  ...props
}) => {
  const theme = useTheme();
  const { isDarkMode } = useColorMode();
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Combine default menu items with custom ones
  const allMenuItems = [
    ...(collapsible ? [{
      label: expanded ? 'Collapse' : 'Expand',
      icon: expanded ? <ExpandLess /> : <ExpandMore />,
      onClick: handleExpandClick,
      disabled: false,
    }] : []),
    ...(onHide ? [{
      label: 'Hide',
      icon: <VisibilityOff />,
      onClick: onHide,
      disabled: false,
    }] : []),
    ...(onFullscreen ? [{
      label: 'Fullscreen',
      icon: <Fullscreen />,
      onClick: onFullscreen,
      disabled: false,
    }] : []),
    ...(menuItems || []),
  ];

  const getCardStyles = () => {
    const baseStyles = {
      borderRadius: tokens.borderRadius.lg,
      backdropFilter: tokens.backdrop.blur.md,
      border: `1px solid ${isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.2)'}`,
      transition: `all ${tokens.animation.duration.normal} ${tokens.animation.easing.inOut}`,
      width: fullWidth ? '100%' : 'auto',
      overflow: 'visible',
      '&:hover': {
        boxShadow: isDarkMode ? tokens.shadow.xl : tokens.shadow.lg,
        transform: 'translateY(-2px)',
        borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.3)',
      },
    };

    switch (variant) {
      case 'glass':
        return {
          ...baseStyles,
          background: isDarkMode 
            ? tokens.components.card.dark.background
            : tokens.components.card.light.background,
          boxShadow: isDarkMode ? tokens.shadow.glass : tokens.shadow.glass,
        };

      case 'elevated':
        return {
          ...baseStyles,
          background: isDarkMode 
            ? 'linear-gradient(145deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.03) 100%)'
            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%)',
          boxShadow: isDarkMode ? tokens.shadow.xl : tokens.shadow.lg,
        };

      case 'minimal':
        return {
          ...baseStyles,
          background: isDarkMode 
            ? 'rgba(255, 255, 255, 0.02)' 
            : 'rgba(255, 255, 255, 0.6)',
          border: `1px solid ${isDarkMode ? tokens.colors.border.dark : tokens.colors.border.light}`,
          boxShadow: tokens.shadow.sm,
        };

      default:
        return {
          ...baseStyles,
          background: isDarkMode 
            ? 'rgba(255, 255, 255, 0.04)' 
            : 'rgba(255, 255, 255, 0.8)',
          boxShadow: isDarkMode ? tokens.shadow.lg : tokens.shadow.base,
        };
    }
  };

  if (loading) {
    return (
      <MuiCard
        className={`card-loading ${className}`}
        sx={{
          ...getCardStyles(),
          ...sx,
        }}
        {...props}
      >
        <CardContent>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            py={4}
          >
            <CircularProgress 
              size={40} 
              sx={{ 
                color: theme.palette.primary.main,
                mb: 2 
              }} 
            />
            <Typography variant="body2" color="text.secondary">
              Loading...
            </Typography>
          </Box>
        </CardContent>
      </MuiCard>
    );
  }

  if (error) {
    return (
      <MuiCard
        className={`card-error ${className}`}
        sx={{
          ...getCardStyles(),
          borderColor: theme.palette.error.main,
          ...sx,
        }}
        {...props}
      >
        <CardContent>
          <Alert 
            severity="error" 
            icon={<ErrorIcon />}
            sx={{
              backgroundColor: 'transparent',
              border: 'none',
              '& .MuiAlert-icon': {
                color: theme.palette.error.main,
              },
            }}
          >
            <Typography variant="body2">
              {typeof error === 'string' ? error : 'An error occurred'}
            </Typography>
          </Alert>
        </CardContent>
      </MuiCard>
    );
  }

  return (
    <MuiCard
      className={`card-${variant} ${className}`}
      sx={{
        ...getCardStyles(),
        ...sx,
      }}
      {...props}
    >
      {(title || icon || allMenuItems.length > 0) && (
        <CardHeader
          avatar={icon}
          title={
            <Typography 
              variant="h6" 
              component="h2"
              sx={{ 
                fontWeight: tokens.typography.fontWeight.semibold,
                color: theme.palette.text.primary,
              }}
            >
              {title}
            </Typography>
          }
          action={
            <Box display="flex" alignItems="center">
              {collapsible && (
                <IconButton
                  onClick={handleExpandClick}
                  aria-expanded={expanded}
                  aria-label="show more"
                  sx={{
                    transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: theme.transitions.create('transform', {
                      duration: theme.transitions.duration.shortest,
                    }),
                    color: theme.palette.text.secondary,
                  }}
                >
                  <ExpandMoreIcon />
                </IconButton>
              )}
              
              {allMenuItems.length > 0 && (
                <>
                  <IconButton
                    onClick={handleMenuClick}
                    aria-label="more options"
                    sx={{ color: theme.palette.text.secondary }}
                  >
                    <MoreVertIcon />
                  </IconButton>
                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                    PaperProps={{
                      sx: {
                        background: isDarkMode 
                          ? 'rgba(255, 255, 255, 0.08)' 
                          : 'rgba(255, 255, 255, 0.9)',
                        backdropFilter: tokens.backdrop.blur.md,
                        border: `1px solid ${isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.2)'}`,
                      },
                    }}
                  >
                    {allMenuItems.map((item, index) => (
                      <MenuItem
                        key={index}
                        onClick={() => {
                          item.onClick();
                          handleMenuClose();
                        }}
                        disabled={item.disabled}
                      >
                        {item.icon && (
                          <Box component="span" sx={{ mr: 1, display: 'flex' }}>
                            {item.icon}
                          </Box>
                        )}
                        {item.label}
                      </MenuItem>
                    ))}
                  </Menu>
                </>
              )}
            </Box>
          }
          sx={{
            pb: title ? 1 : 0,
            '& .MuiCardHeader-content': {
              overflow: 'hidden',
            },
          }}
        />
      )}

      {collapsible ? (
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <CardContent sx={{ pt: title ? 0 : 2 }}>
            {children}
          </CardContent>
        </Collapse>
      ) : (
        <CardContent sx={{ pt: title ? 0 : 2 }}>
          {children}
        </CardContent>
      )}
    </MuiCard>
  );
};

// Loading skeleton component for cards
export const CardSkeleton: React.FC<{ height?: number; lines?: number }> = ({ 
  height = 200, 
  lines = 3 
}) => {
  return (
    <Card variant="glass">
      <Box sx={{ p: 2 }}>
        {/* Title skeleton */}
        <Box
          sx={{
            height: 20,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: tokens.borderRadius.base,
            mb: 2,
            width: '60%',
            animation: 'shimmer 1.5s ease-in-out infinite',
            '@keyframes shimmer': {
              '0%': { opacity: 0.6 },
              '50%': { opacity: 1 },
              '100%': { opacity: 0.6 },
            },
          }}
        />
        
        {/* Content skeleton lines */}
        {Array.from({ length: lines }).map((_, index) => (
          <Box
            key={index}
            sx={{
              height: 16,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: tokens.borderRadius.base,
              mb: 1,
              width: index === lines - 1 ? '40%' : '100%',
              animation: `shimmer 1.5s ease-in-out infinite ${index * 0.2}s`,
              '@keyframes shimmer': {
                '0%': { opacity: 0.6 },
                '50%': { opacity: 1 },
                '100%': { opacity: 0.6 },
              },
            }}
          />
        ))}
        
        {/* Main content skeleton */}
        <Box
          sx={{
            height: height - 100,
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: tokens.borderRadius.base,
            mt: 2,
            animation: 'shimmer 1.5s ease-in-out infinite 0.5s',
            '@keyframes shimmer': {
              '0%': { opacity: 0.6 },
              '50%': { opacity: 1 },
              '100%': { opacity: 0.6 },
            },
          }}
        />
      </Box>
    </Card>
  );
};

export default Card; 