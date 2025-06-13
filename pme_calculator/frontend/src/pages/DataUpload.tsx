import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import { Cloud } from 'lucide-react';
import { useColorMode } from '../contexts/ColorModeContext';
import { EnhancedDataUpload } from '../components/EnhancedDataUpload';

const DataUpload: React.FC = () => {
  const { isDarkMode } = useColorMode();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: isDarkMode ? '#000000' : '#f8fafc',
        pt: 2
      }}
    >
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Fund Analysis Tool - Data Upload
        </Typography>
        <Typography variant="body1" color="text.secondary" mb={3}>
          Upload your fund cashflow and benchmark data to begin comprehensive PME analysis
        </Typography>
        
        <EnhancedDataUpload />
      </Container>
    </Box>
  );
};

export default DataUpload; 