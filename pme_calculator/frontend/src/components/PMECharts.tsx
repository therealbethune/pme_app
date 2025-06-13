import React, { useState } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, ComposedChart,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ReferenceLine, ScatterChart, Scatter
} from 'recharts';
import {
  Box, Typography, Card, CardContent, Tabs, Tab, 
  Grid, FormControl, InputLabel, Select, MenuItem,
  Switch, FormControlLabel, Chip, Divider
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { format, parseISO } from 'date-fns';

interface ChartDataPoint {
  date: string;
  quarter: string;
  tvpi: number;
  dpi: number;
  rvpi: number;
  irr: number;
  nav: number;
  cumulative_contributions: number;
  cumulative_distributions: number;
  cash_flow: number;
  cumulative_net_cash: number;
  total_value: number;
  twr_cumulative?: number;
  years_since_start?: number;
}

interface PMEChartsProps {
  data: {
    performance_timeline?: ChartDataPoint[];
    j_curve_data?: ChartDataPoint[];
    cash_flow_timeline?: ChartDataPoint[];
    twr_data?: ChartDataPoint[];
    metrics: {
      'Fund IRR': number;
      'TVPI': number;
      'DPI': number;
      'RVPI': number;
      pme_metrics?: {
        kaplan_schoar_pme: number;
        benchmark_irr: number;
        alpha: number;
      };
    };
    has_benchmark: boolean;
  };
}

export const PMECharts: React.FC<PMEChartsProps> = ({ data }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState('all');
  const [showBenchmark, setShowBenchmark] = useState(true);

  const isDark = theme.palette.mode === 'dark';
  
  // Color palette for charts
  const colors = {
    primary: '#3b82f6',
    secondary: '#10b981',
    accent: '#f59e0b',
    danger: '#ef4444',
    purple: '#8b5cf6',
    teal: '#06b6d4',
    background: isDark ? '#1f2937' : '#ffffff',
    text: isDark ? '#f3f4f6' : '#1f2937'
  };

  // Format data for different time ranges
  const filterDataByTimeRange = (chartData: ChartDataPoint[] | undefined) => {
    if (!chartData) return [];
    
    const now = new Date();
    let cutoffDate = new Date(0); // Beginning of time
    
    switch (timeRange) {
      case '1y':
        cutoffDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
        break;
      case '3y':
        cutoffDate = new Date(now.getFullYear() - 3, now.getMonth(), now.getDate());
        break;
      case '5y':
        cutoffDate = new Date(now.getFullYear() - 5, now.getMonth(), now.getDate());
        break;
      default:
        return chartData;
    }
    
    return chartData.filter(point => new Date(point.date) >= cutoffDate);
  };

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Card sx={{ p: 2, bgcolor: colors.background, border: `1px solid ${colors.primary}` }}>
          <Typography variant="subtitle2" sx={{ color: colors.text, mb: 1 }}>
            {format(parseISO(label), 'MMM yyyy')}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Box key={index} display="flex" alignItems="center" gap={1}>
              <Box 
                sx={{ 
                  width: 12, 
                  height: 12, 
                  bgcolor: entry.color, 
                  borderRadius: '2px' 
                }} 
              />
              <Typography variant="body2" sx={{ color: colors.text }}>
                {entry.name}: {
                  entry.name.includes('IRR') || entry.name.includes('Alpha') 
                    ? `${(entry.value * 100).toFixed(1)}%`
                    : entry.name.includes('PME') || entry.name.includes('TVPI') || entry.name.includes('DPI')
                    ? `${entry.value.toFixed(2)}x`
                    : entry.name.includes('$') || entry.name.includes('NAV') || entry.name.includes('Cash')
                    ? `$${(entry.value / 1000000).toFixed(1)}M`
                    : entry.value.toFixed(2)
                }
              </Typography>
            </Box>
          ))}
        </Card>
      );
    }
    return null;
  };

  // Performance Timeline Chart
  const PerformanceChart = () => {
    const chartData = filterDataByTimeRange(data.performance_timeline);
    
    return (
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => format(parseISO(date), 'MMM yy')}
            stroke={colors.text}
          />
          <YAxis yAxisId="multiple" stroke={colors.text} />
          <YAxis yAxisId="irr" orientation="right" stroke={colors.text} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          <Line 
            yAxisId="multiple"
            type="monotone" 
            dataKey="tvpi" 
            stroke={colors.primary} 
            strokeWidth={3}
            name="TVPI"
            dot={{ r: 4 }}
          />
          <Line 
            yAxisId="multiple"
            type="monotone" 
            dataKey="dpi" 
            stroke={colors.secondary} 
            strokeWidth={2}
            name="DPI"
          />
          <Line 
            yAxisId="multiple"
            type="monotone" 
            dataKey="rvpi" 
            stroke={colors.accent} 
            strokeWidth={2}
            name="RVPI"
          />
          <Line 
            yAxisId="irr"
            type="monotone" 
            dataKey="irr" 
            stroke={colors.danger} 
            strokeWidth={2}
            name="Fund IRR"
            strokeDasharray="5 5"
          />
          
          {data.has_benchmark && data.metrics.pme_metrics && (
            <ReferenceLine 
              yAxisId="multiple"
              y={data.metrics.pme_metrics.kaplan_schoar_pme} 
              stroke={colors.purple} 
              strokeDasharray="8 8"
              strokeWidth={2}
              label="PME"
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    );
  };

  // J-Curve Analysis Chart
  const JCurveChart = () => {
    const chartData = data.j_curve_data || [];
    
    return (
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
          <XAxis 
            dataKey="years_since_start"
            stroke={colors.text}
            label={{ value: 'Years Since First Investment', position: 'insideBottom', offset: -5 }}
          />
          <YAxis stroke={colors.text} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          <Area
            type="monotone"
            dataKey="cumulative_net_cash"
            stroke={colors.primary}
            fill={colors.primary}
            fillOpacity={0.3}
            name="Cumulative Net Cash Flow"
          />
          <Line
            type="monotone"
            dataKey="total_value"
            stroke={colors.secondary}
            strokeWidth={3}
            name="Total Value (NAV + Distributions)"
          />
          <ReferenceLine y={0} stroke={colors.text} strokeDasharray="2 2" />
        </ComposedChart>
      </ResponsiveContainer>
    );
  };

  // Cash Flow Timeline Chart
  const CashFlowChart = () => {
    const chartData = filterDataByTimeRange(data.cash_flow_timeline);
    
    return (
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => format(parseISO(date), 'MMM yy')}
            stroke={colors.text}
          />
          <YAxis yAxisId="cashflow" stroke={colors.text} />
          <YAxis yAxisId="nav" orientation="right" stroke={colors.text} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          <Bar
            yAxisId="cashflow"
            dataKey="cash_flow"
            fill={colors.secondary}
            name="Net Cash Flow"
          />
          <Line
            yAxisId="nav"
            type="monotone"
            dataKey="nav"
            stroke={colors.purple}
            strokeWidth={2}
            name="NAV"
          />
          <ReferenceLine yAxisId="cashflow" y={0} stroke={colors.text} strokeDasharray="2 2" />
        </ComposedChart>
      </ResponsiveContainer>
    );
  };

  // Performance vs Benchmark Scatter Plot
  const BenchmarkComparison = () => {
    if (!data.has_benchmark || !data.metrics.pme_metrics) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={400}>
          <Typography variant="h6" color="text.secondary">
            Benchmark data required for comparison analysis
          </Typography>
        </Box>
      );
    }

    const scatterData = [
      {
        x: data.metrics.pme_metrics.benchmark_irr * 100,
        y: data.metrics['Fund IRR'] * 100,
        size: data.metrics['TVPI'] * 10,
        name: 'Fund Performance'
      }
    ];

    return (
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
          <XAxis 
            type="number"
            dataKey="x"
            stroke={colors.text}
            label={{ value: 'Benchmark IRR (%)', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            type="number"
            dataKey="y"
            stroke={colors.text}
            label={{ value: 'Fund IRR (%)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Scatter data={scatterData} fill={colors.primary} />
          <ReferenceLine 
            segment={[
              { x: Math.min(...scatterData.map(d => d.x)), y: Math.min(...scatterData.map(d => d.x)) },
              { x: Math.max(...scatterData.map(d => d.x)), y: Math.max(...scatterData.map(d => d.x)) }
            ]}
            stroke={colors.text}
            strokeDasharray="5 5"
            label="Equal Performance"
          />
        </ScatterChart>
      </ResponsiveContainer>
    );
  };

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" fontWeight="bold">
            Advanced Performance Charts
          </Typography>
          
          {/* Chart Controls */}
          <Box display="flex" gap={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={timeRange}
                label="Time Range"
                onChange={(e) => setTimeRange(e.target.value)}
              >
                <MenuItem value="all">All Time</MenuItem>
                <MenuItem value="5y">Last 5 Years</MenuItem>
                <MenuItem value="3y">Last 3 Years</MenuItem>
                <MenuItem value="1y">Last Year</MenuItem>
              </Select>
            </FormControl>
            
            {data.has_benchmark && (
              <FormControlLabel
                control={
                  <Switch
                    checked={showBenchmark}
                    onChange={(e) => setShowBenchmark(e.target.checked)}
                  />
                }
                label="Show Benchmark"
              />
            )}
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Performance Metrics Summary */}
        <Box display="flex" gap={2} flexWrap="wrap" sx={{ mb: 3 }}>
          <Chip 
            label={`Fund IRR: ${(data.metrics['Fund IRR'] * 100).toFixed(1)}%`}
            sx={{ bgcolor: colors.primary, color: 'white', fontWeight: 'bold' }}
          />
          <Chip 
            label={`TVPI: ${data.metrics['TVPI'].toFixed(2)}x`}
            sx={{ bgcolor: colors.secondary, color: 'white', fontWeight: 'bold' }}
          />
          {data.metrics.pme_metrics && (
            <Chip 
              label={`PME: ${data.metrics.pme_metrics.kaplan_schoar_pme.toFixed(2)}x`}
              sx={{ bgcolor: colors.purple, color: 'white', fontWeight: 'bold' }}
            />
          )}
          {data.metrics.pme_metrics && (
            <Chip 
              label={`Alpha: ${(data.metrics.pme_metrics.alpha * 100).toFixed(1)}%`}
              sx={{ 
                bgcolor: data.metrics.pme_metrics.alpha > 0 ? colors.secondary : colors.danger, 
                color: 'white', 
                fontWeight: 'bold' 
              }}
            />
          )}
        </Box>

        {/* Chart Tabs */}
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
          <Tab label="Performance Timeline" />
          <Tab label="J-Curve Analysis" />
          <Tab label="Cash Flow" />
          <Tab label="Benchmark Comparison" />
        </Tabs>

        {/* Chart Content */}
        <Box>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Fund Performance Over Time
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Track TVPI, DPI, RVPI, and IRR progression throughout the fund lifecycle
              </Typography>
              <PerformanceChart />
            </Box>
          )}
          
          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                J-Curve Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Visualize the classic private equity J-curve showing cumulative cash flows vs total value
              </Typography>
              <JCurveChart />
            </Box>
          )}
          
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Cash Flow Timeline
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Analyze cash flow patterns and NAV growth over the investment period
              </Typography>
              <CashFlowChart />
            </Box>
          )}
          
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Performance vs Benchmark
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Compare fund performance against benchmark returns with scatter plot analysis
              </Typography>
              <BenchmarkComparison />
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default PMECharts; 