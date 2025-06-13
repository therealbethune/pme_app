import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { useColorMode } from '../contexts/ColorModeContext';

interface TestingPanelProps {
  visible?: boolean;
  onClose?: () => void;
}

export const TestingPanel: React.FC<TestingPanelProps> = ({ 
  visible = false, 
  onClose 
}) => {
  const { isDarkMode } = useColorMode();

  if (!visible) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 80,
        right: 20,
        width: 300,
        maxHeight: 'calc(100vh - 100px)',
        overflow: 'auto',
        zIndex: 1300,
        backgroundColor: isDarkMode ? '#000000' : '#ffffff',
        border: `1px solid ${isDarkMode ? '#333' : '#e0e0e0'}`,
        borderRadius: 2,
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
      }}
    >
      <Card sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Dev Panel</Typography>
            <Button size="small" onClick={onClose}>
              Close
            </Button>
          </Box>

          <Typography variant="caption" color="textSecondary">
            Quick Navigation:
          </Typography>
          <Box display="flex" flexDirection="column" gap={1} mt={1}>
            <Button 
              size="small" 
              onClick={() => window.location.href = '/upload'}
              variant="outlined"
              fullWidth
            >
              Data Upload
            </Button>
            <Button 
              size="small" 
              onClick={() => window.location.href = '/analysis'}
              variant="outlined"
              fullWidth
            >
              Analysis
            </Button>
          </Box>

          <Divider sx={{ my: 2 }} />
          
          <Typography variant="caption" color="textSecondary">
            Debug Info:
          </Typography>
          <Box mt={1}>
            <Typography variant="body2" color="textSecondary">
              Environment: {process.env.NODE_ENV || 'development'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Theme: {isDarkMode ? 'Dark' : 'Light'}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}; 