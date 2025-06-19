import React, { useEffect, useRef } from 'react';

declare global {
  interface Window {
    Plotly: any;
  }
}

interface PlotlyChartProps {
  data: any[];
  layout: any;
  config?: any;
  className?: string;
  onLoad?: () => void;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
  data,
  layout,
  config = {},
  className = '',
  onLoad
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const plotlyLoadedRef = useRef(false);

  useEffect(() => {
    const loadPlotly = async () => {
      if (window.Plotly) {
        plotlyLoadedRef.current = true;
        createChart();
        return;
      }

      try {
        // Load Plotly from CDN
        const script = document.createElement('script');
        script.src = 'https://cdn.plot.ly/plotly-2.26.0.min.js';
        script.onload = () => {
          plotlyLoadedRef.current = true;
          createChart();
          onLoad?.();
        };
        script.onerror = () => {
          console.error('Failed to load Plotly');
        };
        document.head.appendChild(script);
      } catch (error) {
        console.error('Error loading Plotly:', error);
      }
    };

    const createChart = () => {
      if (!chartRef.current || !window.Plotly || !plotlyLoadedRef.current) return;

      // Dark theme layout defaults
      const darkLayout = {
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { 
          color: '#ffffff', 
          family: 'Inter, Arial, sans-serif',
          size: 12
        },
        legend: {
          bgcolor: 'rgba(0,0,0,0)',
          bordercolor: 'rgba(255,255,255,0.2)',
          borderwidth: 1,
          font: { color: '#ffffff' }
        },
        xaxis: {
          gridcolor: 'rgba(255,255,255,0.1)',
          linecolor: 'rgba(255,255,255,0.2)',
          tickcolor: 'rgba(255,255,255,0.2)',
          titlefont: { color: '#ffffff' },
          tickfont: { color: '#ffffff' }
        },
        yaxis: {
          gridcolor: 'rgba(255,255,255,0.1)',
          linecolor: 'rgba(255,255,255,0.2)',
          tickcolor: 'rgba(255,255,255,0.2)',
          titlefont: { color: '#ffffff' },
          tickfont: { color: '#ffffff' }
        },
        title: {
          font: { color: '#ffffff' }
        },
        ...layout
      };

      const defaultConfig = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        toImageButtonOptions: {
          format: 'png',
          filename: 'pme-analysis-chart',
          height: 500,
          width: 800,
          scale: 1
        },
        ...config
      };

      window.Plotly.newPlot(chartRef.current, data, darkLayout, defaultConfig);
    };

    loadPlotly();

    return () => {
      if (chartRef.current && window.Plotly) {
        window.Plotly.purge(chartRef.current);
      }
    };
  }, [data, layout, config, onLoad]);

  return (
    <div 
      ref={chartRef} 
      className={`w-full h-full min-h-[400px] ${className}`}
      style={{ minHeight: '400px' }}
    />
  );
}; 