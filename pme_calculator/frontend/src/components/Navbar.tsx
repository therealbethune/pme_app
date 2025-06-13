import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { DarkModeToggle } from './DarkModeToggle';
import { useColorMode } from '../contexts/ColorModeContext';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { isDarkMode } = useColorMode();

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar 
      position="sticky" 
      color="default" 
      elevation={1}
      sx={{ 
        borderBottom: '1px solid',
        borderBottomColor: 'divider',
        backgroundColor: isDarkMode ? 'rgba(18, 18, 20, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            textDecoration: 'none',
            color: isDarkMode ? '#3b82f6' : 'primary.main',
            fontWeight: 600,
            flexGrow: 1,
            transition: 'color 0.2s ease-in-out',
            '&:hover': {
              color: isDarkMode ? '#60a5fa' : 'primary.dark',
            },
          }}
        >
          Fund Analysis Tool
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button
            component={RouterLink}
            to="/upload"
            color="inherit"
            variant={isActive('/upload') || isActive('/') ? 'contained' : 'text'}
            size="small"
            sx={{ 
              fontWeight: isActive('/upload') || isActive('/') ? 600 : 400,
              minWidth: 'auto',
            }}
          >
            Data Upload
          </Button>
          
          <Button
            component={RouterLink}
            to="/analysis"
            color="inherit"
            variant={isActive('/analysis') ? 'contained' : 'text'}
            size="small"
            sx={{ 
              fontWeight: isActive('/analysis') ? 600 : 400,
            }}
          >
            Analysis
          </Button>
          
          <Button
            component={RouterLink}
            to="/charts-test"
            color="inherit"
            variant={isActive('/charts-test') ? 'contained' : 'text'}
            size="small"
            sx={{ 
              fontWeight: isActive('/charts-test') ? 600 : 400,
              fontSize: '0.75rem',
            }}
          >
            Charts Test
          </Button>
          
          <DarkModeToggle />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 