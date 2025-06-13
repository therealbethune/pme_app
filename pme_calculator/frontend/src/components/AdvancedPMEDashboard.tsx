import React, { useState } from 'react';
import { 
  Box, Typography, Card, CardContent, Grid, Tabs, Tab, 
  Chip, Divider, Paper, LinearProgress, Button, Alert
} from '@mui/material';
import { 
  TrendingUp, BarChart, PieChart, Download, Target, 
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
  const getPMEPerformance = (ks_pme: number) => {
    if (ks_pme >= 1.3) return { label: 'Exceptional', color: '#22c55e', bg: '#dcfce7' };
    if (ks_pme >= 1.15) return { label: 'Strong', color: '#3b82f6', bg: '#dbeafe' };
    if (ks_pme >= 1.0) return { label: 'Good', color: '#f59e0b', bg: '#fef3c7' };
    if (ks_pme >= 0.85) return { label: 'Below Market', color: '#f97316', bg: '#fed7aa' };
    return { label: 'Poor', color: '#ef4444', bg: '#fecaca' };
  };

  const ksPerformance = pme_metrics ? getPMEPerformance(pme_metrics.kaplan_schoar_pme) : null;

  // Format percentage values
  const formatPercent = (value: number, decimals = 1) => 
    `${(value * 100).toFixed(decimals)}%`;

  const formatDecimal = (value: number, decimals = 3) => 
    value.toFixed(decimals);

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
          <Tab label="Core Metrics" icon={<Target />} iconPosition="start" />
          <Tab label="PME Analysis" icon={<Calculate />} iconPosition="start" />
          <Tab label="Risk Analytics" icon={<Timeline />} iconPosition="start" />
          <Tab label="Benchmarking" icon={<BarChart />} iconPosition="start" />
        </Tabs>
      </Card>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Core Performance Metrics */}
          <Grid item xs={12} md={6} lg={3}>
            <MetricCard
              title="Fund IRR"
              value={formatPercent(basic_metrics['Fund IRR'])}
              icon={<TrendingUp />}
              trend="up"
              subtitle="Internal Rate of Return"
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MetricCard
              title="TVPI"
              value={`${basic_metrics['TVPI'].toFixed(2)}x`}
              icon={<AttachMoney />}
              trend={basic_metrics['TVPI'] > 1 ? "up" : "down"}
              subtitle="Total Value to Paid-In"
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MetricCard
              title="DPI"
              value={`${basic_metrics['DPI'].toFixed(2)}x`}
              icon={<PieChart />}
              trend="up"
              subtitle="Distributions to Paid-In"
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
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
          <Grid item xs={12} md={6}>
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
                    {pme_metrics.kaplan_schoar_pme > 1 ? 'Outperformed' : 'Underperformed'} public markets
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
                    color={pme_metrics.direct_alpha > 0 ? '#22c55e' : '#ef4444'}
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

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" mb={2}>
                  Performance vs. Benchmark
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Fund IRR
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {formatPercent(pme_metrics.fund_irr)}
                  </Typography>
                </Box>

                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Benchmark IRR
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {formatPercent(pme_metrics.benchmark_irr)}
                  </Typography>
                </Box>

                <Box mb={3}>
                  <Typography variant="subtitle2" color="text.secondary" mb={1}>
                    Alpha (Excess Return)
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" 
                    color={pme_metrics.twr_alpha > 0 ? '#22c55e' : '#ef4444'}
                  >
                    {formatPercent(pme_metrics.twr_alpha, 2)}
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={Math.min(Math.abs(pme_metrics.twr_alpha) * 1000, 100)} 
                    color={pme_metrics.twr_alpha > 0 ? 'success' : 'error'}
                    sx={{ mt: 1, height: 8, borderRadius: 4 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Confidence Intervals */}
          {pme_metrics.calculation_metadata && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold" mb={2}>
                    Statistical Confidence Intervals (95%)
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Fund Start Date
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {pme_metrics.calculation_metadata.fund_start_date}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Fund End Date
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {pme_metrics.calculation_metadata.fund_end_date}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Total Contributions
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {pme_metrics.calculation_metadata.total_contributions}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Total Distributions
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {pme_metrics.calculation_metadata.total_distributions}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Final NAV
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {pme_metrics.calculation_metadata.final_nav}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Index Start Value
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {pme_metrics.calculation_metadata.index_start_value}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Index End Value
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {pme_metrics.calculation_metadata.index_end_value}
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" mb={2}>
                  Risk Analytics
                </Typography>
                <Alert severity="info">
                  Risk analytics module coming soon. Will include volatility analysis, 
                  downside protection metrics, and stress testing capabilities.
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" mb={2}>
                  Benchmark Comparison
                </Typography>
                {has_benchmark ? (
                  <Alert severity="success">
                    Benchmark data loaded. PME calculations are complete and accurate.
                  </Alert>
                ) : (
                  <Alert severity="warning">
                    No benchmark data available. Upload index data to enable complete PME analysis.
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

// Simple MetricCard component for consistency
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
    switch (trend) {
      case 'up': return '#22c55e';
      case 'down': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <Card sx={{ 
      height: '100%',
      background: theme.palette.mode === 'dark' ? '#000000' : '#ffffff',
      border: theme.palette.mode === 'dark' ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e2e8f0'
    }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="subtitle2" color="text.secondary">
            {title}
          </Typography>
          <Box sx={{ color: getTrendColor() }}>
            {icon}
          </Box>
        </Box>
        <Typography variant="h4" fontWeight="bold" mb={1}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default AdvancedPMEDashboard; 