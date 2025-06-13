import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import PlotlyChart from './PlotlyChart';

interface ChartsDashboardProps {
  analysisComplete?: boolean;
}

export const ChartsDashboard: React.FC<ChartsDashboardProps> = ({ 
  analysisComplete = false 
}) => {
  if (!analysisComplete) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Charts Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Please upload fund and index data and run analysis to view charts.
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Performance Analytics Dashboard
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* First Row - Main Performance Charts */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flex: 1, minWidth: '400px' }}>
            <PlotlyChart
              title="Cash Flow Overview"
              url="/v1/metrics/cashflow_overview"
              height={400}
            />
          </Box>
          
          <Box sx={{ flex: 1, minWidth: '400px' }}>
            <PlotlyChart
              title="Net Cash Flow vs Market"
              url="/v1/metrics/net_cf_market"
              height={400}
            />
          </Box>
        </Box>

        {/* Second Row - IRR and PME Analysis */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flex: 1, minWidth: '400px' }}>
            <PlotlyChart
              title="IRR vs PME Analysis"
              url="/v1/metrics/irr_pme"
              height={400}
            />
          </Box>

          <Box sx={{ flex: 1, minWidth: '400px' }}>
            <PlotlyChart
              title="PME Progression Over Time"
              url="/v1/metrics/pme_progression"
              height={400}
            />
          </Box>
        </Box>

        {/* Third Row - Performance Comparison */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flex: 1, minWidth: '400px' }}>
            <PlotlyChart
              title="TWR vs Index Performance"
              url="/v1/metrics/twr_vs_index"
              height={400}
            />
          </Box>

          <Box sx={{ flex: 1, minWidth: '400px' }}>
            <PlotlyChart
              title="Cash Flow Pacing Analysis"
              url="/v1/metrics/cashflow_pacing"
              height={400}
            />
          </Box>
        </Box>
      </Box>
    </Container>
  );
};

export default ChartsDashboard; 