import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  useTheme,
  Card,
  CardContent
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
  ComposedChart
} from 'recharts';
import { format, subYears, startOfYear, parseISO } from 'date-fns';

interface AnalyticsData {
  performance_timeline: Array<{
    date: string;
    tvpi: number;
    dpi: number;
    rvpi: number;
    irr: number;
    nav: number;
    cumulative_contributions: number;
    cumulative_distributions: number;
  }>;
  j_curve_data: Array<{
    date: string;
    years_since_start: number;
    cumulative_net_cash: number;
    nav: number;
    total_value: number;
    days_since_start: number;
  }>;
  twr_data: Array<{
    date: string;
    twr_cumulative: number;
    period_return: number;
    nav: number;
    start_nav?: number;
    cash_flow?: number;
  }>;
  nav_waterfall: {
    components: Array<{
      category: string;
      value: number;
      type: 'starting' | 'positive' | 'negative' | 'ending';
    }>;
    summary: {
      start_nav: number;
      end_nav: number;
      total_change: number;
      total_contributions: number;
      total_distributions: number;
    };
  };
  cash_flow_timeline: Array<{
    date: string;
    quarter: string;
    contributions: number;
    distributions: number;
    net_flow: number;
    rolling_4q_net: number;
    nav: number;
  }>;
  date_range: {
    start_date: string;
    end_date: string;
    fund_life_days: number;
  };
}

interface AnalyticsDashboardProps {
  data: AnalyticsData;
}

type DateRange = 'all' | '10y' | '5y' | '3y' | '1y' | 'ytd';

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ data }) => {
  const theme = useTheme();
  const [dateRange, setDateRange] = useState<DateRange>('all');
  const [performanceMetrics, setPerformanceMetrics] = useState({
    tvpi: true,
    dpi: true,
    rvpi: true,
    irr: true
  });

  // Load saved preferences from localStorage
  useEffect(() => {
    const savedRange = localStorage.getItem('analytics_date_range') as DateRange;
    if (savedRange) {
      setDateRange(savedRange);
    }
    
    const savedMetrics = localStorage.getItem('analytics_enabled_metrics');
    if (savedMetrics) {
      setPerformanceMetrics(JSON.parse(savedMetrics));
    }
  }, []);

  // Save preferences to localStorage
  useEffect(() => {
    localStorage.setItem('analytics_date_range', dateRange);
    localStorage.setItem('analytics_enabled_metrics', JSON.stringify(performanceMetrics));
  }, [dateRange, performanceMetrics]);

  // Helper function to get start date based on selected range
  const getStartDate = (): Date => {
    if (dateRange === 'all') return new Date(0);

    const endDate = new Date(data.date_range.end_date);
    
    switch (dateRange) {
      case '10y':
        return new Date(endDate.getFullYear() - 10, endDate.getMonth(), endDate.getDate());
      case '5y':
        return new Date(endDate.getFullYear() - 5, endDate.getMonth(), endDate.getDate());
      case '3y':
        return new Date(endDate.getFullYear() - 3, endDate.getMonth(), endDate.getDate());
      case '1y':
        return new Date(endDate.getFullYear() - 1, endDate.getMonth(), endDate.getDate());
      case 'ytd':
        return new Date(endDate.getFullYear(), 0, 1);
      default:
        return new Date(0);
    }
  };

  // Filter data based on selected date range
  const filteredData = React.useMemo(() => {
    const startDate = getStartDate();
    
    const filterByDate = (items: any[]) => 
      items.filter(item => {
        try {
          const itemDate = parseISO(item.date || item.period || item.quarter);
          return itemDate >= startDate;
        } catch (error) {
          return true;
        }
      });

    return {
      performance_timeline: filterByDate(data.performance_timeline || []),
      j_curve_data: data.j_curve_data || [],
      twr_data: filterByDate(data.twr_data || []),
      nav_waterfall: data.nav_waterfall || { components: [] },
      cash_flow_timeline: filterByDate(data.cash_flow_timeline || [])
    };
  }, [data, dateRange]);

  // Enhanced formatters
  const currencyCompactFormatter = (value: number) => {
    if (value === undefined || value === null || isNaN(value)) return '$0';
    return new Intl.NumberFormat('en-US', {
      notation: 'compact',
      compactDisplay: 'short',
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 1
    }).format(value);
  };

  const percentFormatter = (value: number) => {
    if (value === undefined || value === null || isNaN(value)) return '0%';
    // Check if value is already in percentage format (>1) or decimal format (<1)
    const percentValue = Math.abs(value) > 1 ? value : value * 100;
    return `${percentValue.toFixed(1)}%`;
  };

  const multipleFormatter = (value: number) => {
    if (value === undefined || value === null || isNaN(value)) return '0.0x';
    return `${value.toFixed(2)}x`;
  };

  const yearAxisFormatter = (value: number) => {
    if (value === undefined || value === null || isNaN(value)) return '0';
    return `${value.toFixed(1)}y`;
  };

  const safeDateFormat = (dateValue: any, formatString: string): string => {
    try {
      if (!dateValue) return 'Invalid Date';
      
      let dateToFormat: Date;
      if (typeof dateValue === 'string') {
        dateToFormat = parseISO(dateValue);
      } else if (dateValue instanceof Date) {
        dateToFormat = dateValue;
      } else {
        return 'Invalid Date';
      }
      
      if (isNaN(dateToFormat.getTime())) {
        return 'Invalid Date';
      }
      
      return format(dateToFormat, formatString);
    } catch (error) {
      return 'Invalid Date';
    }
  };

  // Enhanced tooltip component
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Paper sx={{ 
          p: 2, 
          backgroundColor: theme.palette.background.paper, 
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: theme.shadows[8],
          borderRadius: 2
        }}>
          <Typography variant="body2" fontWeight="600" mb={1} color="text.primary">
            {safeDateFormat(label, 'MMM dd, yyyy')}
          </Typography>
          {payload.map((entry: any, index: number) => {
            let formattedValue = entry.value;
            
            // Format based on data type
            if (entry.dataKey === 'irr') {
              // IRR is likely already in percentage format
              formattedValue = `${entry.value.toFixed(2)}%`;
            } else if (entry.dataKey?.includes('twr') || entry.dataKey?.includes('period_return')) {
              // TWR data is already in percentage format
              formattedValue = `${entry.value.toFixed(2)}%`;
            } else if (['tvpi', 'dpi', 'rvpi'].includes(entry.dataKey)) {
              formattedValue = multipleFormatter(entry.value);
            } else if (entry.dataKey?.includes('years')) {
              formattedValue = yearAxisFormatter(entry.value);
            } else {
              formattedValue = currencyCompactFormatter(entry.value);
            }

            return (
              <Typography 
                key={index} 
                variant="body2" 
                sx={{ color: entry.color, mb: 0.5 }}
              >
                <strong>{entry.name}:</strong> {formattedValue}
              </Typography>
            );
          })}
        </Paper>
      );
    }
    return null;
  };

  // Process cash flow data
  const cashFlowData = filteredData.cash_flow_timeline.map(item => ({
    ...item,
    distributions_negative: -Math.abs(item.distributions || 0)
  }));

  return (
    <Box sx={{ p: 3 }}>
      {/* Simplified Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Portfolio Analytics Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Comprehensive performance analysis and insights
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <InputLabel>Time Period</InputLabel>
              <Select
                value={dateRange}
                label="Time Period"
                onChange={(e) => setDateRange(e.target.value as DateRange)}
              >
                <MenuItem value="all">Since Inception</MenuItem>
                <MenuItem value="10y">10 Years</MenuItem>
                <MenuItem value="5y">5 Years</MenuItem>
                <MenuItem value="3y">3 Years</MenuItem>
                <MenuItem value="1y">1 Year</MenuItem>
                <MenuItem value="ytd">YTD</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Paper>

      {/* Charts Container */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        
        {/* Performance Metrics Chart */}
        <Card elevation={3} sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight="600">
                Performance Metrics Over Time
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                {Object.entries(performanceMetrics).map(([key, enabled]) => (
                  <FormControlLabel
                    key={key}
                    control={
                      <Switch
                        size="small"
                        checked={enabled}
                        onChange={(e) => setPerformanceMetrics(prev => ({
                          ...prev,
                          [key]: e.target.checked
                        }))}
                      />
                    }
                    label={key.toUpperCase()}
                    sx={{ m: 0 }}
                  />
                ))}
              </Box>
            </Box>
            
            <ResponsiveContainer width="100%" height={420}>
              <ComposedChart data={filteredData.performance_timeline} margin={{ top: 20, right: 40, left: 20, bottom: 80 }}>
                <CartesianGrid 
                  strokeDasharray="2 2" 
                  stroke={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}
                />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => safeDateFormat(value, 'MMM yy')}
                  stroke={theme.palette.text.secondary}
                  fontSize={11}
                  tick={{ fontSize: 11 }}
                />
                <YAxis 
                  yAxisId="multiples"
                  domain={['dataMin - 0.1', 'dataMax + 0.1']}
                  tickFormatter={multipleFormatter}
                  stroke={theme.palette.text.secondary}
                  fontSize={11}
                  tick={{ fontSize: 11 }}
                  label={{ value: 'Multiples', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                />
                <YAxis 
                  yAxisId="percentages"
                  orientation="right"
                  domain={['dataMin - 5', 'dataMax + 5']}
                  tickFormatter={(value) => `${value.toFixed(1)}%`}
                  stroke={theme.palette.text.secondary}
                  fontSize={11}
                  tick={{ fontSize: 11 }}
                  label={{ value: 'IRR %', angle: 90, position: 'insideRight', style: { textAnchor: 'middle' } }}
                />
                <Tooltip content={<CustomTooltip />} />
                
                {performanceMetrics.tvpi && (
                  <Line
                    yAxisId="multiples"
                    type="monotone"
                    dataKey="tvpi"
                    stroke="#6366f1"
                    name="TVPI"
                    strokeWidth={2.5}
                    dot={false}
                  />
                )}
                {performanceMetrics.dpi && (
                  <Line
                    yAxisId="multiples"
                    type="monotone"
                    dataKey="dpi"
                    stroke="#10b981"
                    name="DPI"
                    strokeWidth={2.5}
                    dot={false}
                  />
                )}
                {performanceMetrics.rvpi && (
                  <Line
                    yAxisId="multiples"
                    type="monotone"
                    dataKey="rvpi"
                    stroke="#f59e0b"
                    name="RVPI"
                    strokeWidth={2.5}
                    dot={false}
                  />
                )}
                {performanceMetrics.irr && (
                  <Line
                    yAxisId="percentages"
                    type="monotone"
                    dataKey="irr"
                    stroke="#ef4444"
                    name="IRR"
                    strokeWidth={2.5}
                    strokeDasharray="4 4"
                    dot={false}
                  />
                )}
                
                <Brush 
                  dataKey="date" 
                  height={50} 
                  stroke={theme.palette.primary.main}
                  tickFormatter={(value) => safeDateFormat(value, 'MMM yy')}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Second Row: J-Curve and TWR */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          
          {/* J-Curve */}
          <Card elevation={3} sx={{ flex: 1, minWidth: '400px', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="600" mb={3}>
                J-Curve Analysis
              </Typography>
              
                             <ResponsiveContainer width="100%" height={380}>
                 <AreaChart data={filteredData.j_curve_data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                   <CartesianGrid 
                     strokeDasharray="2 2" 
                     stroke={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}
                   />
                   <XAxis 
                     dataKey="years_since_start" 
                     stroke={theme.palette.text.secondary}
                     fontSize={11}
                     tick={{ fontSize: 11 }}
                     tickFormatter={yearAxisFormatter}
                     label={{ value: 'Years Since Start', position: 'insideBottom', offset: -10, style: { textAnchor: 'middle' } }}
                   />
                   <YAxis 
                     domain={['dataMin - 1000000', 'dataMax + 1000000']}
                     tickFormatter={currencyCompactFormatter}
                     stroke={theme.palette.text.secondary}
                     fontSize={11}
                     tick={{ fontSize: 11 }}
                     label={{ value: 'Cumulative Cash Flow', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                   />
                  
                  <ReferenceLine y={0} stroke={theme.palette.divider} strokeWidth={1.5} strokeDasharray="3 3" />
                  <Tooltip content={<CustomTooltip />} />
                  
                  <Area
                    type="monotone"
                    dataKey="cumulative_net_cash"
                    stroke="#6366f1"
                    fill="url(#jCurveGradient)"
                    strokeWidth={2}
                  />
                  
                  <defs>
                    <linearGradient id="jCurveGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0.05}/>
                    </linearGradient>
                  </defs>
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Time-Weighted Return */}
          <Card elevation={3} sx={{ flex: 1, minWidth: '400px', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="600" mb={3}>
                Time-Weighted Return
              </Typography>
              
                             <ResponsiveContainer width="100%" height={380}>
                 <LineChart data={filteredData.twr_data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                   <CartesianGrid 
                     strokeDasharray="2 2" 
                     stroke={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}
                   />
                   <XAxis 
                     dataKey="date" 
                     tickFormatter={(value) => safeDateFormat(value, 'MMM yy')}
                     stroke={theme.palette.text.secondary}
                     fontSize={11}
                     tick={{ fontSize: 11 }}
                   />
                   <YAxis 
                     domain={['dataMin - 10', 'dataMax + 10']}
                     tickFormatter={(value) => `${value.toFixed(1)}%`}
                     stroke={theme.palette.text.secondary}
                     fontSize={11}
                     tick={{ fontSize: 11 }}
                     label={{ value: 'Return %', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                   />
                  <Tooltip content={<CustomTooltip />} />
                  
                  <Line
                    type="monotone"
                    dataKey="twr_cumulative"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={false}
                    name="Fund TWR"
                  />
                  
                  <Brush 
                    dataKey="date" 
                    height={50} 
                    stroke={theme.palette.primary.main}
                    tickFormatter={(value) => safeDateFormat(value, 'MMM yy')}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>

        {/* Third Row: Waterfall and Cash Flow */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          
          {/* NAV Waterfall */}
          <Card elevation={3} sx={{ flex: 1, minWidth: '400px', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="600" mb={3}>
                NAV Waterfall
              </Typography>
              
                             <ResponsiveContainer width="100%" height={380}>
                 <BarChart data={filteredData.nav_waterfall?.components || []} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                   <CartesianGrid 
                     strokeDasharray="2 2" 
                     stroke={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}
                   />
                   <XAxis 
                     dataKey="category" 
                     stroke={theme.palette.text.secondary}
                     angle={0}
                     textAnchor="middle"
                     height={60}
                     interval={0}
                     fontSize={10}
                     tick={{ fontSize: 10 }}
                     tickFormatter={(value) => {
                       const labels: { [key: string]: string } = {
                         'Beginning NAV': 'Begin NAV',
                         'Contributions': 'Contrib.',
                         'Distributions': 'Distrib.',
                         'Unrealized Gain/Loss': 'Unrealized',
                         'Fees/Expenses': 'Fees',
                         'Ending NAV': 'End NAV'
                       };
                       return labels[value] || value;
                     }}
                   />
                   <YAxis 
                     domain={['dataMin - 5000000', 'dataMax + 5000000']}
                     tickFormatter={currencyCompactFormatter}
                     stroke={theme.palette.text.secondary}
                     fontSize={11}
                     tick={{ fontSize: 11 }}
                     label={{ value: 'NAV ($)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                   />
                  <Tooltip content={<CustomTooltip />} />
                  
                  <Bar
                    dataKey="value"
                    fill="#6366f1"
                    radius={[2, 2, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Cash Flow */}
          <Card elevation={3} sx={{ flex: 1, minWidth: '400px', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="600" mb={3}>
                Cash Flow Analysis
              </Typography>
              
                             <ResponsiveContainer width="100%" height={380}>
                 <ComposedChart data={cashFlowData} margin={{ top: 20, right: 40, left: 20, bottom: 60 }}>
                   <CartesianGrid 
                     strokeDasharray="2 2" 
                     stroke={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}
                   />
                   <XAxis 
                     dataKey="quarter" 
                     stroke={theme.palette.text.secondary}
                     fontSize={10}
                     tick={{ fontSize: 10 }}
                   />
                   <YAxis 
                     yAxisId="cashflow"
                     domain={['dataMin - 2000000', 'dataMax + 2000000']}
                     tickFormatter={currencyCompactFormatter}
                     stroke={theme.palette.text.secondary}
                     fontSize={11}
                     tick={{ fontSize: 11 }}
                     label={{ value: 'Cash Flow ($)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                   />
                   <YAxis 
                     yAxisId="cumulative"
                     orientation="right"
                     domain={['dataMin - 1000000', 'dataMax + 1000000']}
                     tickFormatter={currencyCompactFormatter}
                     stroke={theme.palette.text.secondary}
                     fontSize={11}
                     tick={{ fontSize: 11 }}
                     label={{ value: 'Rolling 4Q Net ($)', angle: 90, position: 'insideRight', style: { textAnchor: 'middle' } }}
                   />
                  
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine yAxisId="cashflow" y={0} stroke={theme.palette.divider} strokeWidth={1} />
                  
                  <Bar
                    yAxisId="cashflow"
                    dataKey="contributions"
                    fill="#10b981"
                    name="Contributions"
                    radius={[2, 2, 0, 0]}
                  />
                  
                  <Bar
                    yAxisId="cashflow"
                    dataKey="distributions_negative"
                    fill="#ef4444"
                    name="Distributions"
                    radius={[0, 0, 2, 2]}
                  />
                  
                  <Line
                    yAxisId="cumulative"
                    type="monotone"
                    dataKey="rolling_4q_net"
                    stroke="#6366f1"
                    strokeWidth={3}
                    dot={false}
                    name="Rolling 4Q Net"
                  />
                  
                  <Brush 
                    dataKey="quarter" 
                    height={50} 
                    stroke={theme.palette.primary.main}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default AnalyticsDashboard; 