import React, { useEffect, useRef, useState } from 'react';
import { Box, Card, CardContent, Typography, CircularProgress } from '@mui/material';

// Declare Plotly as a global variable
declare global {
  interface Window {
    Plotly: any;
    makeChart: (elementId: string, url: string) => Promise<void>;
    API_BASE?: string;
  }
}

interface PlotlyChartProps {
  title: string;
  url: string;
  height?: number;
  loading?: boolean;
  error?: string;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
  title,
  url,
  height = 400,
  loading = false,
  error
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartId = useRef(`chart-${Math.random().toString(36).substr(2, 9)}`);
  const [isLoading, setIsLoading] = useState(true);
  const [chartError, setChartError] = useState<string | null>(null);

  useEffect(() => {
    const loadChart = async () => {
      if (!chartRef.current || loading || error) return;

      try {
        setIsLoading(true);
        setChartError(null);

        // Wait for Plotly to be available
        let attempts = 0;
        while (!window.Plotly && attempts < 50) {
          await new Promise(resolve => setTimeout(resolve, 100));
          attempts++;
        }

        if (!window.Plotly) {
          throw new Error('Plotly library failed to load');
        }

        // Set the ID on the chart div
        chartRef.current.id = chartId.current;

        // Check if makeChart function is available
        if (typeof window.makeChart === 'function') {
          await window.makeChart(chartId.current, url);
        } else {
          // Fallback: Load chart data directly and use Plotly
          const API_BASE = window.API_BASE || `${location.protocol}//${location.hostname}:8000`;
          const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
          
          console.log(`Loading chart data from: ${fullUrl}`);
          
          const response = await fetch(fullUrl);
          if (!response.ok) {
            throw new Error(`Failed to fetch chart data: ${response.status} ${response.statusText}`);
          }
          
          const chartData = await response.json();
          console.log(`Chart data received:`, chartData);
          
          // Apply professional styling
          const layout = {
            ...chartData.layout,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
              family: '"Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
              size: 12,
              color: '#e0e6ed'
            },
            margin: { l: 60, r: 20, t: 40, b: 40 },
            xaxis: {
              ...chartData.layout?.xaxis,
              gridcolor: 'rgba(255,255,255,0.1)',
              linecolor: 'rgba(255,255,255,0.2)',
              tickcolor: 'rgba(255,255,255,0.2)',
              tickfont: { color: '#b0b7c3', size: 11 },
              titlefont: { color: '#e0e6ed', size: 13 }
            },
            yaxis: {
              ...chartData.layout?.yaxis,
              gridcolor: 'rgba(255,255,255,0.1)',
              linecolor: 'rgba(255,255,255,0.2)',
              tickcolor: 'rgba(255,255,255,0.2)',
              tickfont: { color: '#b0b7c3', size: 11 },
              titlefont: { color: '#e0e6ed', size: 13 }
            }
          };

          const config = {
            responsive: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d']
          };

          console.log(`Rendering chart with Plotly.newPlot`);
          await window.Plotly.newPlot(chartId.current, chartData.data, layout, config);
          console.log(`Chart ${title} rendered successfully`);
        }
        
        setIsLoading(false);
      } catch (err) {
        console.error(`Error loading chart ${title}:`, err);
        setChartError(err instanceof Error ? err.message : 'Unknown error occurred');
        setIsLoading(false);
      }
    };

    loadChart();
  }, [title, url, loading, error]);

  if (loading || isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Box 
            display="flex" 
            justifyContent="center" 
            alignItems="center" 
            height={height}
          >
            <Box textAlign="center">
              <CircularProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Loading chart...
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error || chartError) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Box 
            display="flex" 
            justifyContent="center" 
            alignItems="center" 
            height={height}
            color="error.main"
          >
            <div style={{ textAlign: 'center' }}>
              <div>⚠️ Error loading chart</div>
              <small>{error || chartError}</small>
            </div>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box height={height}>
          <div 
            ref={chartRef}
            style={{ 
              width: '100%', 
              height: '100%',
              minHeight: `${height}px`
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default PlotlyChart; 