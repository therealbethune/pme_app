import React, { useState } from 'react';
import { 
  Box, Typography, Card, CardContent, Tabs, Tab, 
  Chip, Divider, Paper, LinearProgress, Button, Alert
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { 
  TrendingUp, BarChart, PieChart, Download, Adjust, 
  AttachMoney, Calculate, EmojiEvents, Timeline
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface PMEMetrics {
  kaplan_schoar_pme?: number;
  pme_plus_lambda?: number;
  direct_alpha?: number;
  long_nickels_pme_irr?: number;
  fund_irr?: number;
  benchmark_irr?: number;
  fund_twr?: number;
  index_twr?: number;
  twr_alpha?: number;
  outperformance?: boolean;
  calculation_metadata?: {
    aligned_periods: number;
    fund_start_date: string;
    fund_end_date: string;
    total_contributions: number;
    total_distributions: number;
    final_nav: number;
    index_start_value: number;
    index_end_value: number;
  };
}

interface AdvancedAnalysis {
  success: boolean;
  basic_metrics: {
    'Fund IRR': number;
    'TVPI': number;
    'DPI': number;
    'RVPI': number;
    'MOIC': number;
  };
  pme_metrics?: PMEMetrics;
  analysis_date: string;
  has_benchmark: boolean;
}

interface AdvancedPMEDashboardProps {
  data: AdvancedAnalysis;
  onExport: () => void;
}

export const AdvancedPMEDashboard: React.FC<AdvancedPMEDashboardProps> = ({ 
  data, 
  onExport 
}) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);

  const { basic_metrics, pme_metrics, has_benchmark } = data;

  // PME Performance Assessment
  const getPMEPerformance = (ks_pme: number | undefined) => {
    if (ks_pme === undefined) return { label: 'N/A', color: '#9ca3af', bg: '#f3f4f6' };
    if (ks_pme >= 1.3) return { label: 'Exceptional', color: '#22c55e', bg: '#dcfce7' };
    if (ks_pme >= 1.15) return { label: 'Strong', color: '#3b82f6', bg: '#dbeafe' };
    if (ks_pme >= 1.0) return { label: 'Good', color: '#f59e0b', bg: '#fef3c7' };
    if (ks_pme >= 0.85) return { label: 'Below Market', color: '#f97316', bg: '#fed7aa' };
    return { label: 'Poor', color: '#ef4444', bg: '#fecaca' };
  };

  const ksPerformance = pme_metrics ? getPMEPerformance(pme_metrics.kaplan_schoar_pme) : { label: 'N/A', color: '#9ca3af', bg: '#f3f4f6' };

  // Format percentage values
  const formatPercent = (value: number | undefined, decimals = 1) => {
    if (value === undefined) return 'N/A';
    return `${(value * 100).toFixed(decimals)}%`;
  };

  const formatDecimal = (value: number | undefined, decimals = 3) => {
    if (value === undefined) return 'N/A';
    return value.toFixed(decimals);
  };

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header Section */}
      <Card sx={{ 
        mb: 3, 
        background: theme.palette.mode === 'dark' ? '#000000' : '#ffffff',
        border: theme.palette.mode === 'dark' ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e2e8f0'
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Typography variant="h4" fontWeight="bold" display="flex" alignItems="center" gap={1}>
                <EmojiEvents sx={{ color: '#3b82f6' }} />
                Institutional PME Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" mt={1}>
                Professional-grade performance measurement and benchmarking
              </Typography>
            </Box>
            <Box display="flex" gap={2}>
              {ksPerformance && (
                <Chip 
                  label={ksPerformance.label}
                  sx={{ 
                    backgroundColor: ksPerformance.bg,
                    color: ksPerformance.color,
                    fontWeight: 'bold'
                  }}
                />
              )}
              <Button 
                variant="outlined" 
                startIcon={<Download />}
                onClick={onExport}
              >
                Export Report
              </Button>
            </Box>
          </Box>

          {!has_benchmark && (
            <Alert severity="info" sx={{ mb: 2 }}>
              PME calculations require benchmark data. Upload index data for complete analysis.
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Navigation Tabs */}
      <Card sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Core Metrics" icon={<Adjust />} iconPosition="start" />
          <Tab label="PME Analysis" icon={<Calculate />} iconPosition="start" />
          <Tab label="Risk Analytics" icon={<Timeline />} iconPosition="start" />
          <Tab label="Benchmarking" icon={<BarChart />} iconPosition="start" />
        </Tabs>
      </Card>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Core Performance Metrics */}
          <Grid xs={12} md={6} lg={3}>
            <MetricCard
              title="Fund IRR"
              value={formatPercent(basic_metrics['Fund IRR'])}
              icon={<TrendingUp />}
              trend="up"
              subtitle="Internal Rate of Return"
            />
          </Grid>
          <Grid xs={12} md={6} lg={3}>
            <MetricCard
              title="TVPI"
              value={`${basic_metrics['TVPI'].toFixed(2)}x`}
              icon={<AttachMoney />}
              trend={basic_metrics['TVPI'] > 1 ? "up" : "down"}
              subtitle="Total Value to Paid-In"
            />
          </Grid>
          <Grid xs={12} md={6} lg={3}>
            <MetricCard
              title="DPI"
              value={`${basic_metrics['DPI'].toFixed(2)}x`}
              icon={<PieChart />}
              trend="up"
              subtitle="Distributions to Paid-In"
            />
          </Grid>
          <Grid xs={12} md={6} lg={3}>
            <MetricCard
              title="RVPI"
              value={`${basic_metrics['RVPI'].toFixed(2)}x`}
              icon={<BarChart />}
              trend="neutral"
              subtitle="Residual Value to Paid-In"
            />
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && pme_metrics && (
        <Grid container spacing={3}>
          {/* PME Metrics */}
          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" mb={2}>
                  Public Market Equivalent (PME) Metrics
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Kaplan-Schoar PME
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color={ksPerformance?.color}>
                    {formatDecimal(pme_metrics.kaplan_schoar_pme)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {pme_metrics.kaplan_schoar_pme && pme_metrics.kaplan_schoar_pme > 1 ? 'Outperformed' : 'Underperformed'} public markets
                  </Typography>
                </Box>

                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    PME+ Lambda (Burgiss Method)
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {formatDecimal(pme_metrics.pme_plus_lambda)}
                  </Typography>
                </Box>

                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Direct Alpha
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" 
                    color={pme_metrics.direct_alpha && pme_metrics.direct_alpha > 0 ? '#22c55e' : '#ef4444'}
                  >
                    {formatPercent(pme_metrics.direct_alpha, 2)}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Long-Nickels PME
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {formatDecimal(pme_metrics.long_nickels_pme_irr)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" mb={2}>
                  Performance vs. Benchmark
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Fund vs. Benchmark IRR
                  </Typography>
                  <Box display="flex" alignItems="baseline" gap={2}>
                    <Box>
                      <Typography variant="h5" fontWeight="bold">
                        {formatPercent(pme_metrics.fund_irr)}
                      </Typography>
                      <Typography variant="caption">Fund IRR</Typography>
                    </Box>
                    <Typography color="text.secondary">vs.</Typography>
                    <Box>
                      <Typography variant="h5" fontWeight="bold">
                        {formatPercent(pme_metrics.benchmark_irr)}
                      </Typography>
                      <Typography variant="caption">Benchmark IRR</Typography>
                    </Box>
                  </Box>
                </Box>
                
                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Time-Weighted Alpha
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" 
                    color={pme_metrics.twr_alpha && pme_metrics.twr_alpha > 0 ? '#22c55e' : '#ef4444'}
                  >
                    {formatPercent(pme_metrics.twr_alpha, 2)}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={pme_metrics.twr_alpha ? Math.min(Math.abs(pme_metrics.twr_alpha) * 1000, 100) : 0}
                    color={pme_metrics.twr_alpha && pme_metrics.twr_alpha > 0 ? 'success' : 'error'}
                    sx={{ height: 8, borderRadius: 4, mt: 1 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" mb={2}>PME Calculation Details</Typography>
                <Divider sx={{ mb: 2 }}/>
                {pme_metrics && pme_metrics.calculation_metadata && (
                  <Grid container spacing={2}>
                    <Grid xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                        <Typography variant="subtitle2" color="text.secondary">Alignment & Period</Typography>
                        <Typography>Aligned Periods: {pme_metrics.calculation_metadata.aligned_periods}</Typography>
                        <Typography>Fund Start: {pme_metrics.calculation_metadata.fund_start_date}</Typography>
                        <Typography>Fund End: {pme_metrics.calculation_metadata.fund_end_date}</Typography>
                      </Paper>
                    </Grid>
                    <Grid xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                        <Typography variant="subtitle2" color="text.secondary">Fund Cash Flows</Typography>
                        <Typography>Contributions: {formatCurrency(pme_metrics.calculation_metadata.total_contributions)}</Typography>
                        <Typography>Distributions: {formatCurrency(pme_metrics.calculation_metadata.total_distributions)}</Typography>
                        <Typography>Final NAV: {formatCurrency(pme_metrics.calculation_metadata.final_nav)}</Typography>
                      </Paper>
                    </Grid>
                    <Grid xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                        <Typography variant="subtitle2" color="text.secondary">Benchmark Data</Typography>
                        <Typography>Index Start Value: {formatDecimal(pme_metrics.calculation_metadata.index_start_value, 2)}</Typography>
                        <Typography>Index End Value: {formatDecimal(pme_metrics.calculation_metadata.index_end_value, 2)}</Typography>
                      </Paper>
                    </Grid>
                    <Grid xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                        <Typography variant="subtitle2" color="text.secondary">Outperformance</Typography>
                        <Typography color={pme_metrics.outperformance === true ? "success.main" : pme_metrics.outperformance === false ? "error.main" : "text.secondary"}>
                          {pme_metrics.outperformance === true ? 'Yes' : pme_metrics.outperformance === false ? 'No' : 'N/A'}
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h5" fontWeight="bold">Risk Analytics</Typography>
                <Typography color="text.secondary">Monte Carlo simulations, stress tests, and other risk metrics will be displayed here.</Typography>
                <Box sx={{ my: 4, textAlign: 'center' }}>
                  <Timeline sx={{ fontSize: '4rem', color: 'primary.main' }} />
                  <Typography variant="h6" mt={2}>Coming Soon</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h5" fontWeight="bold">Advanced Benchmarking</Typography>
                <Typography color="text.secondary">Compare against various public and private benchmarks.</Typography>
                <Box sx={{ my: 4, textAlign: 'center' }}>
                  <BarChart sx={{ fontSize: '4rem', color: 'primary.main' }} />
                  <Typography variant="h6" mt={2}>Coming Soon</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  trend: 'up' | 'down' | 'neutral';
  subtitle?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon, trend, subtitle }) => {
  const theme = useTheme();

  const getTrendColor = () => {
    if (trend === 'up') return theme.palette.success.main;
    if (trend === 'down') return theme.palette.error.main;
    return theme.palette.text.secondary;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="start">
          <Box>
            <Typography variant="body1" color="text.secondary">{title}</Typography>
            <Typography variant="h4" fontWeight="bold" mt={1}>{value}</Typography>
            {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
          </Box>
          <Box sx={{ color: getTrendColor() }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AdvancedPMEDashboard; 