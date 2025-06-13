import React from 'react';
import { IconButton, useTheme, Tooltip } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useColorMode } from '../contexts/ColorModeContext';

export const DarkModeToggle: React.FC = () => {
  const theme = useTheme();
  const { toggleColorMode, isDarkMode } = useColorMode();

  return (
    <Tooltip title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}>
      <IconButton 
        onClick={toggleColorMode} 
        color="inherit"
        size="medium"
        sx={{
          ml: 1,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: theme.palette.action.hover,
          },
        }}
      >
        {isDarkMode ? (
          <Brightness7Icon sx={{ color: theme.palette.text.primary }} />
        ) : (
          <Brightness4Icon sx={{ color: theme.palette.text.primary }} />
        )}
      </IconButton>
    </Tooltip>
  );
}; 