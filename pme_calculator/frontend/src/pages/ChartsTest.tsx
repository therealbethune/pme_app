import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Alert, Button } from '@mui/material';
import PlotlyChart from '../components/PlotlyChart';

const ChartsTest: React.FC = () => {
  const [plotlyStatus, setPlotlyStatus] = useState<string>('Checking...');
  const [apiStatus, setApiStatus] = useState<string>('Checking...');

  useEffect(() => {
    // Check Plotly availability
    const checkPlotly = () => {
      if (typeof window !== 'undefined') {
        if (window.Plotly) {
          setPlotlyStatus(`✅ Plotly loaded (version: ${window.Plotly.version || 'unknown'})`);
        } else {
          setPlotlyStatus('❌ Plotly not available');
        }
      }
    };

    // Check API availability
    const checkAPI = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health');
        if (response.ok) {
          const data = await response.json();
          setApiStatus(`✅ API healthy (${data.service})`);
        } else {
          setApiStatus(`❌ API error: ${response.status}`);
        }
      } catch (error) {
        setApiStatus(`❌ API unreachable: ${error}`);
      }
    };

    checkPlotly();
    checkAPI();

    // Recheck Plotly after a delay in case it's still loading
    const timer = setTimeout(checkPlotly, 2000);
    return () => clearTimeout(timer);
  }, []);

  const testDirectPlotly = () => {
    if (window.Plotly) {
      const testData = [{
        x: [1, 2, 3, 4],
        y: [10, 11, 12, 13],
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Test Data'
      }];
      
      const layout = {
        title: 'Direct Plotly Test',
        xaxis: { title: 'X Axis' },
        yaxis: { title: 'Y Axis' }
      };

      window.Plotly.newPlot('direct-plotly-test', testData, layout);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Charts Test & Debug Page
      </Typography>
      
      <Box sx={{ mb: 4 }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="h6">System Status</Typography>
          <Typography>Plotly: {plotlyStatus}</Typography>
          <Typography>API: {apiStatus}</Typography>
          <Typography>API Base: {window.API_BASE || 'Not set'}</Typography>
        </Alert>
        
        <Button variant="outlined" onClick={testDirectPlotly} sx={{ mb: 2 }}>
          Test Direct Plotly
        </Button>
        
        <div id="direct-plotly-test" style={{ height: '300px', border: '1px solid #ccc', marginBottom: '20px' }}></div>
      </Box>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Testing Plotly chart integration with API data
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <PlotlyChart
          title="TWR vs Index Performance"
          url="/v1/metrics/twr_vs_index"
          height={400}
        />
        
        <PlotlyChart
          title="Cash Flow Overview"
          url="/v1/metrics/cashflow_overview"
          height={400}
        />
      </Box>
    </Container>
  );
};

export default ChartsTest; 