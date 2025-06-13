import React from 'react';
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Container,
  Chip
} from '@mui/material';
import {
  Error,
  Refresh,
  FlashOn,
  TrendingUp,
  Settings,
  OpenInNew,
  CheckCircle,
  Cancel,
  Info,
  Warning
} from '@mui/icons-material';

// Professional glassfunds-style error component for API connection issues
export const ApiConnectionError: React.FC<{
  onRetry?: () => void;
  onSwitchToDemo?: () => void;
}> = ({ onRetry, onSwitchToDemo }) => (
  <Box
    sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f5f5 0%, #e3f2fd 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      p: 3
    }}
  >
    <Container maxWidth="sm">
      <Card
        sx={{
          borderRadius: 4,
          boxShadow: 4,
          textAlign: 'center'
        }}
      >
        <CardContent sx={{ p: 4 }}>
          {/* Professional icon */}
          <Box
            sx={{
              width: 64,
              height: 64,
              bgcolor: 'primary.light',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 3
            }}
          >
            <Error sx={{ fontSize: 32, color: 'primary.main' }} />
          </Box>

          {/* Professional heading */}
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
            Backend Connection Required
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.6 }}>
            The PME Calculator requires the Python backend to be running for full functionality. 
            Please start the backend service or try our demo mode.
          </Typography>

          {/* Professional action buttons */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 4 }}>
            <Button
              onClick={onRetry}
              variant="contained"
              startIcon={<Refresh />}
              size="large"
              fullWidth
              sx={{ py: 1.5 }}
            >
              Retry Connection
            </Button>
            
            <Button
              onClick={onSwitchToDemo}
              variant="outlined"
              startIcon={<FlashOn />}
              size="large"
              fullWidth
              sx={{ py: 1.5 }}
            >
              Switch to Demo Mode
            </Button>
          </Box>

          {/* Help section */}
          <Box sx={{ pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Need help getting started?
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button
                size="small"
                startIcon={<Settings />}
                sx={{ textTransform: 'none', fontSize: '0.75rem' }}
              >
                Setup Guide
              </Button>
              <Button
                size="small"
                startIcon={<OpenInNew />}
                sx={{ textTransform: 'none', fontSize: '0.75rem' }}
              >
                Documentation
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Glassfunds branding */}
      <Box sx={{ textAlign: 'center', mt: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Powered by <strong>glassfunds</strong> technology
        </Typography>
      </Box>
    </Container>
  </Box>
);

// Professional demo mode banner
export const DemoModeBanner: React.FC<{
  onConnectBackend?: () => void;
}> = ({ onConnectBackend }) => (
  <Alert
    severity="warning"
    icon={<FlashOn />}
    sx={{
      borderRadius: 0,
      justifyContent: 'center',
      '& .MuiAlert-message': {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
        maxWidth: '1200px'
      }
    }}
  >
    <Box>
      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
        Demo Mode Active
      </Typography>
      <Typography variant="caption">
        Using sample data - Connect backend for full functionality
      </Typography>
    </Box>
    <Button size="small" variant="text" sx={{ ml: 2 }} onClick={onConnectBackend}>
      Connect Backend →
    </Button>
  </Alert>
);

// Professional loading state for glassfunds
export const GlassfundsLoader: React.FC<{
  message?: string;
  fullScreen?: boolean;
}> = ({ 
  message = "Loading PME Calculator...", 
  fullScreen = false 
}) => {
  const content = (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: fullScreen ? '100vh' : '16rem',
        background: 'linear-gradient(135deg, #f5f5f5 0%, #e3f2fd 100%)'
      }}
    >
      <Box sx={{ textAlign: 'center' }}>
        {/* Glassfunds-style animated logo */}
        <Box sx={{ position: 'relative', mb: 3 }}>
          <Card
            sx={{
              width: 64,
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              borderRadius: 4
            }}
          >
            <TrendingUp sx={{ fontSize: 32, color: 'primary.main' }} />
          </Card>
        </Box>

        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'medium' }}>
          {message}
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
          <CircularProgress size={24} />
        </Box>

        <Typography variant="body2" color="text.secondary">
          Preparing advanced analytics platform
        </Typography>
      </Box>
    </Box>
  );

  return fullScreen ? (
    <Box sx={{ position: 'fixed', inset: 0, zIndex: 9999 }}>
      {content}
    </Box>
  ) : content;
};

// Professional "coming soon" placeholder for features
export const ComingSoonFeature: React.FC<{
  title: string;
  description: string;
}> = ({ title, description }) => (
  <Card sx={{ p: 3, textAlign: 'center', opacity: 0.7 }}>
    <FlashOn sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
    <Typography variant="h6" gutterBottom>
      {title}
    </Typography>
    <Typography variant="body2" color="text.secondary" gutterBottom>
      {description}
    </Typography>
    <Chip
      label="Coming Soon"
      size="small"
      sx={{ mt: 1 }}
      color="primary"
      variant="outlined"
    />
  </Card>
);

// Professional status indicator
export const StatusIndicator: React.FC<{
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  compact?: boolean;
}> = ({ status, message, compact = false }) => {
  const getIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'error':
        return <Cancel sx={{ color: 'error.main' }} />;
      case 'warning':
        return <Warning sx={{ color: 'warning.main' }} />;
      case 'info':
        return <Info sx={{ color: 'info.main' }} />;
      default:
        return <Info />;
    }
  };

  const getColor = () => {
    switch (status) {
      case 'success':
        return 'success.main';
      case 'error':
        return 'error.main';
      case 'warning':
        return 'warning.main';
      case 'info':
        return 'info.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        p: compact ? 1 : 2,
        borderRadius: 1,
        bgcolor: `${status}.light`,
        border: 1,
        borderColor: `${status}.main`,
        opacity: 0.9
      }}
    >
      {getIcon()}
      <Typography
        variant={compact ? 'body2' : 'body1'}
        sx={{ color: getColor(), fontWeight: 'medium' }}
      >
        {message}
      </Typography>
    </Box>
  );
};

export const LoadingState: React.FC<{ message?: string }> = ({ message = "Loading..." }) => (
  <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
    <div className="text-center">
      <GlassfundsLoader />
      <p className="mt-4 text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  </div>
);

export const EmptyState: React.FC<{
  title: string;
  description: string;
  icon?: React.ReactNode;
}> = ({ title, description, icon }) => (
  <div className="text-center py-12">
    {icon && <div className="flex justify-center mb-4">{icon}</div>}
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{title}</h3>
    <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">{description}</p>
  </div>
); 