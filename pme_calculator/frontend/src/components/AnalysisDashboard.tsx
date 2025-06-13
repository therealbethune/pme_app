import React from 'react';
import { 
  Box, Typography, Card, CardContent, Divider, Chip, 
  Button, Paper, LinearProgress, Container, useTheme 
} from '@mui/material';
import { 
  TrendingUp, DollarSign, Target, 
  Download, PieChart
} from 'lucide-react';
import { MetricCard } from './MetricCard';
import CashOnCashAnalysis from './CashOnCashAnalysis';
import CashFlowAnalysis from './CashFlowAnalysis';
import AnalyticsDashboard from './AnalyticsDashboard';

interface AnalysisData {
  success: boolean;
  metrics: {
    'Fund IRR': number;
    'TVPI': number;
    'MOIC': number;
    'DPI': number;
    'RVPI': number;
    'Total Contributions': number;
    'Total Distributions': number;
    'Final NAV': number;
    'Cash-on-Cash Analysis'?: {
      overall_metrics: {
        total_cash_on_cash_return: number;
        cash_yield: number;
        unrealized_return: number;
        annualized_cash_yield: number;
        fund_life_years: number;
      };
      quarterly_breakdown: Array<{
        quarter: string;
        contributions: number;
        distributions: number;
        nav: number;
        cumulative_contributions: number;
        cumulative_distributions: number;
        cash_on_cash_return: number;
        cash_returned_ratio: number;
        unrealized_ratio: number;
      }>;
      insights: {
        performance_status: string;
        cash_efficiency: string;
        distribution_pattern: string;
        key_observations: string[];
      };
    };
    'Cash Flow Analysis'?: {
      velocity_metrics: {
        deployment_velocity: number;
        distribution_velocity: number;
        net_cash_flow_velocity: number;
        deployment_period_years: number;
        distribution_period_years: number;
      };
      j_curve_analysis: {
        j_curve_depth: number;
        time_to_bottom_years: number;
        time_to_positive_years: number | null;
        current_cumulative_cash: number;
        j_curve_recovery: number;
      };
      net_cash_flow_timeline: Array<{
        date: string;
        cash_flow: number;
        cumulative_net_cash: number;
        nav: number;
        total_value: number;
      }>;
      distribution_pattern: {
        total_distribution_events: number;
        average_distribution_size: number;
        distribution_frequency: number;
        distribution_consistency: string;
        largest_distribution: number;
        distribution_timing: string;
      };
      deployment_analysis: {
        total_deployment_events: number;
        average_deployment_size: number;
        deployment_frequency: number;
        deployment_pattern: string;
        largest_deployment: number;
      };
      efficiency_metrics: {
        capital_efficiency: number;
        time_efficiency: number;
        cash_generation_rate: number;
        nav_growth_rate: number;
      };
      insights: {
        velocity_assessment: string;
        j_curve_status: string;
        cash_flow_health: string;
        key_observations: string[];
      };
    };
    'Analytics Data'?: {
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
    };
  };
  has_benchmark: boolean;
  analysis_date: string;
  summary: any;
}

interface AnalysisDashboardProps {
  data: AnalysisData;
  onExport: () => void;
}

export const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({ data, onExport }) => {
  const { metrics } = data;
  const theme = useTheme();
  
  // Determine performance categories
  const getPerformanceStatus = (irr: number, tvpi: number) => {
    if (irr > 0.15 && tvpi > 1.5) return { label: 'Excellent', color: '#22c55e', trend: 'up' as const };
    if (irr > 0.10 && tvpi > 1.2) return { label: 'Good', color: '#3b82f6', trend: 'up' as const };
    if (irr > 0.05 && tvpi > 1.0) return { label: 'Fair', color: '#f59e0b', trend: 'neutral' as const };
    return { label: 'Poor', color: '#ef4444', trend: 'down' as const };
  };

  const performance = getPerformanceStatus(metrics['Fund IRR'], metrics['TVPI']);
  
  // Calculate some derived metrics
  const totalValue = metrics['Total Distributions'] + metrics['Final NAV'];
  const realizationRate = metrics['Total Distributions'] / totalValue;

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      {/* Enhanced Header Section */}
      <Card sx={{ 
        mb: 2.5, 
        background: theme.palette.mode === 'dark' 
          ? '#000000'
          : 'background.paper',
        border: theme.palette.mode === 'dark' 
          ? '1px solid rgba(255,255,255,0.1)'
          : '1px solid',
        borderColor: theme.palette.mode === 'dark' 
          ? 'rgba(255,255,255,0.1)'
          : 'divider',
        position: 'relative',
        overflow: 'hidden',
        '&::before': theme.palette.mode === 'dark' ? {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.08) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(139, 92, 246, 0.05) 0%, transparent 50%)',
          backdropFilter: 'blur(10px)',
        } : {}
      }}>
        <CardContent sx={{ p: 2.5, position: 'relative', zIndex: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                <Box 
                  sx={{ 
                    p: 1, 
                    borderRadius: '10px', 
                    backgroundColor: 'primary.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <TrendingUp size={24} color="white" />
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  PME Analysis Results
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                <Chip 
                  label={performance.label}
                  size="small"
                  sx={{ 
                    backgroundColor: performance.color + '20',
                    color: performance.color,
                    fontWeight: 'bold',
                    border: `1px solid ${performance.color}40`
                  }}
                />
                <Typography variant="body2" color="text.secondary" fontWeight="medium">
                  Analysis completed on {new Date(data.analysis_date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                  })}
                </Typography>
              </Box>
            </Box>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={onExport}
              size="medium"
            >
              Export Report
            </Button>
          </Box>

          {/* Quick Stats Summary */}
          <Box 
            display="grid" 
            gridTemplateColumns={{ xs: 'repeat(2, 1fr)', sm: 'repeat(4, 1fr)' }} 
            gap={2}
            mt={2}
          >
            <Paper sx={{ p: 1.5, textAlign: 'center', backgroundColor: 'background.default' }}>
              <Typography variant="h6" fontWeight="bold" color="primary.main">
                {(metrics['Fund IRR'] * 100).toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                IRR
              </Typography>
            </Paper>
            <Paper sx={{ p: 1.5, textAlign: 'center', backgroundColor: 'background.default' }}>
              <Typography variant="h6" fontWeight="bold" color="primary.main">
                {metrics['TVPI'].toFixed(2)}x
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Multiple
              </Typography>
            </Paper>
            <Paper sx={{ p: 1.5, textAlign: 'center', backgroundColor: 'background.default' }}>
              <Typography variant="h6" fontWeight="bold" color="primary.main">
                {metrics['DPI'].toFixed(2)}x
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Distributions
              </Typography>
            </Paper>
            <Paper sx={{ p: 1.5, textAlign: 'center', backgroundColor: 'background.default' }}>
              <Typography variant="h6" fontWeight="bold" color="primary.main">
                {(realizationRate * 100).toFixed(0)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Realized
              </Typography>
            </Paper>
          </Box>
        </CardContent>
      </Card>

      {/* Key Performance Metrics */}
      <Box mb={2.5}>
        <Typography variant="h6" fontWeight="bold" mb={2}>
          Key Performance Metrics
        </Typography>
        <Box 
          display="grid" 
          gridTemplateColumns={{ 
            xs: '1fr', 
            sm: 'repeat(2, 1fr)', 
            md: 'repeat(4, 1fr)' 
          }} 
          gap={2}
        >
          <MetricCard
            title="Internal Rate of Return"
            value={metrics['Fund IRR']}
            formatAsPercent
            icon={<TrendingUp size={20} />}
            trend={performance.trend}
            description="The annualized effective compound return rate"
          />
          <MetricCard
            title="Total Value to Paid-In"
            value={metrics['TVPI']}
            formatAsMultiple
            icon={<Target size={20} />}
            trend={metrics['TVPI'] > 1.2 ? 'up' : metrics['TVPI'] > 1.0 ? 'neutral' : 'down'}
            description="Total value returned relative to capital invested"
          />
          <MetricCard
            title="Distributions to Paid-In"
            value={metrics['DPI']}
            formatAsMultiple
            icon={<DollarSign size={20} />}
            trend={metrics['DPI'] > 1.0 ? 'up' : 'neutral'}
            description="Cash distributions relative to capital invested"
          />
          <MetricCard
            title="Residual Value to Paid-In"
            value={metrics['RVPI']}
            formatAsMultiple
            icon={<PieChart size={20} />}
            trend="neutral"
            description="Remaining NAV relative to capital invested"
          />
        </Box>
      </Box>

      {/* Cash-on-Cash Return Analysis */}
      {metrics['Cash-on-Cash Analysis'] && (
        <CashOnCashAnalysis data={metrics['Cash-on-Cash Analysis']} />
      )}

      {/* Cash Flow Analysis */}
      {metrics['Cash Flow Analysis'] && (
        <CashFlowAnalysis data={metrics['Cash Flow Analysis']} />
      )}

      {/* Interactive Analytics Dashboard */}
      {metrics['Analytics Data'] && (
        <AnalyticsDashboard data={metrics['Analytics Data']} />
      )}

      {/* Enhanced Investment Summary */}
      <Box display="flex" flexDirection={{ xs: 'column', md: 'row' }} gap={2} mb={2.5}>
        <Box flex={2}>
          <Card sx={{ 
            background: theme.palette.mode === 'dark' 
              ? '#000000'
              : 'background.paper',
            border: theme.palette.mode === 'dark' 
              ? '1px solid rgba(255,255,255,0.1)'
              : '1px solid',
            borderColor: theme.palette.mode === 'dark' 
              ? 'rgba(255,255,255,0.1)'
              : 'divider',
            position: 'relative',
            overflow: 'hidden',
            '&::before': theme.palette.mode === 'dark' ? {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'radial-gradient(circle at 30% 30%, rgba(239, 68, 68, 0.05) 0%, transparent 50%), radial-gradient(circle at 70% 70%, rgba(34, 197, 94, 0.05) 0%, transparent 50%)',
              backdropFilter: 'blur(10px)',
            } : {}
          }}>
            <CardContent sx={{ p: 4, position: 'relative', zIndex: 1 }}>
              <Box display="flex" alignItems="center" gap={2} mb={4}>
                <Box 
                  sx={{ 
                    p: 1.5, 
                    borderRadius: '12px', 
                    backgroundColor: 'primary.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <DollarSign size={24} color="white" />
                </Box>
                <Typography variant="h5" fontWeight="bold">
                  Investment Flow Summary
                </Typography>
              </Box>

              <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(180px, 1fr))" gap={2} mb={3}>
                <Paper sx={{ 
                  p: 2, 
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%)'
                    : 'background.default',
                  border: 1, 
                  borderColor: theme.palette.mode === 'dark' 
                    ? 'rgba(239, 68, 68, 0.2)'
                    : 'error.main', 
                  borderRadius: 2,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 32px rgba(239, 68, 68, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                    : 'none',
                }}>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Box sx={{ p: 1, borderRadius: '8px', backgroundColor: 'error.main' }}>
                      <Download size={16} color="white" />
                    </Box>
                    <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.9)' : 'error.main'} fontWeight="bold">
                      CAPITAL INVESTED
                    </Typography>
                  </Box>
                  <Typography variant="h5" fontWeight="bold" color={theme.palette.mode === 'dark' ? '#ef4444' : 'error.main'} mb={1}>
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD',
                      minimumFractionDigits: 0,
                    }).format(metrics['Total Contributions'])}
                  </Typography>
                  <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'}>
                    Total capital committed to fund
                  </Typography>
                </Paper>

                <Paper sx={{ 
                  p: 2, 
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%)'
                    : 'background.default',
                  border: 1, 
                  borderColor: theme.palette.mode === 'dark' 
                    ? 'rgba(34, 197, 94, 0.2)'
                    : 'success.main', 
                  borderRadius: 2,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 32px rgba(34, 197, 94, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                    : 'none',
                }}>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Box sx={{ p: 1, borderRadius: '8px', backgroundColor: 'success.main' }}>
                      <TrendingUp size={16} color="white" />
                    </Box>
                    <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.9)' : 'success.main'} fontWeight="bold">
                      CASH RETURNED
                    </Typography>
                  </Box>
                  <Typography variant="h5" fontWeight="bold" color={theme.palette.mode === 'dark' ? '#22c55e' : 'success.main'} mb={1}>
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD',
                      minimumFractionDigits: 0,
                    }).format(metrics['Total Distributions'])}
                  </Typography>
                  <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'}>
                    Distributions received to date
                  </Typography>
                </Paper>

                <Paper sx={{ 
                  p: 2, 
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%)'
                    : 'background.default',
                  border: 1, 
                  borderColor: theme.palette.mode === 'dark' 
                    ? 'rgba(59, 130, 246, 0.2)'
                    : 'primary.main', 
                  borderRadius: 2,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 32px rgba(59, 130, 246, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                    : 'none',
                }}>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Box sx={{ p: 1, borderRadius: '8px', backgroundColor: 'primary.main' }}>
                      <PieChart size={16} color="white" />
                    </Box>
                    <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.9)' : 'primary.main'} fontWeight="bold">
                      REMAINING NAV
                    </Typography>
                  </Box>
                  <Typography variant="h5" fontWeight="bold" color={theme.palette.mode === 'dark' ? '#3b82f6' : 'primary.main'} mb={1}>
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD',
                      minimumFractionDigits: 0,
                    }).format(metrics['Final NAV'])}
                  </Typography>
                  <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'}>
                    Current unrealized portfolio value
                  </Typography>
                </Paper>
              </Box>
              
              <Paper sx={{ 
                p: 2, 
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%)'
                  : 'background.default',
                border: 1, 
                borderColor: theme.palette.mode === 'dark' 
                  ? 'rgba(168, 85, 247, 0.2)'
                  : 'divider',
                boxShadow: theme.palette.mode === 'dark'
                  ? '0 8px 32px rgba(168, 85, 247, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                  : 'none',
              }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6" fontWeight="bold" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.9)' : 'inherit'}>
                    Capital Realization Progress
                  </Typography>
                  <Chip
                    label={`${(realizationRate * 100).toFixed(1)}% Realized`}
                    sx={{ 
                      backgroundColor: performance.color + '20',
                      color: performance.color,
                      fontWeight: 'bold'
                    }}
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={realizationRate * 100}
                  sx={{ 
                    height: 12, 
                    borderRadius: 6,
                    backgroundColor: 'action.hover',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: performance.color,
                      borderRadius: 6,
                    }
                  }}
                />
                <Box display="flex" justifyContent="space-between" mt={1}>
                  <Typography variant="caption" color="text.secondary">
                    0%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    100% Realized
                  </Typography>
                </Box>
              </Paper>
            </CardContent>
          </Card>
        </Box>
        
        <Box flex={1}>
          <Card 
            sx={{ 
              height: '100%',
              background: theme.palette.mode === 'dark' 
                ? '#000000'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              position: 'relative',
              overflow: 'hidden',
              border: theme.palette.mode === 'dark' 
                ? '1px solid rgba(255,255,255,0.1)'
                : 'none',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: theme.palette.mode === 'dark'
                  ? 'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%)'
                  : 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
                backdropFilter: 'blur(10px)',
              }
            }}
          >
            <CardContent sx={{ p: 2.5, position: 'relative', zIndex: 1 }}>
              <Box display="flex" alignItems="center" gap={1.5} mb={2.5}>
                <Box 
                  sx={{ 
                    p: 1, 
                    borderRadius: '10px', 
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? 'rgba(255,255,255,0.1)' 
                      : 'rgba(255,255,255,0.2)',
                    backdropFilter: 'blur(10px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <TrendingUp size={20} color="white" />
                </Box>
                <Typography variant="h6" fontWeight="bold" color="white">
                  Performance Summary
                </Typography>
              </Box>
              
              <Box display="flex" flexDirection="column" gap={2}>
                {/* Multiple of Invested Capital */}
                <Box 
                  sx={{ 
                    p: 2,
                    borderRadius: '12px',
                    background: theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%)'
                      : 'rgba(255,255,255,0.15)',
                    backdropFilter: 'blur(20px)',
                    border: theme.palette.mode === 'dark'
                      ? '1px solid rgba(59, 130, 246, 0.2)'
                      : '1px solid rgba(255,255,255,0.2)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 8px 32px rgba(59, 130, 246, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                      : 'none',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: theme.palette.mode === 'dark'
                        ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(139, 92, 246, 0.2) 100%)'
                        : 'rgba(255,255,255,0.25)',
                      transform: 'translateY(-2px)',
                      boxShadow: theme.palette.mode === 'dark'
                        ? '0 12px 40px rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                        : '0 4px 20px rgba(0,0,0,0.1)',
                    }
                  }}
                >
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Target size={20} color="rgba(255,255,255,0.8)" />
                    <Typography variant="body2" color="rgba(255,255,255,0.9)" fontWeight="500">
                      Multiple of Invested Capital
                    </Typography>
                  </Box>
                  <Typography variant="h4" fontWeight="bold" color="rgba(255,255,255,0.95)">
                    {metrics['MOIC'].toFixed(2)}x
                  </Typography>
                  <Typography variant="caption" color="rgba(255,255,255,0.7)">
                    Total returns as multiple of investment
                  </Typography>
                </Box>

                {/* Total Value Created */}
                <Box 
                  sx={{ 
                    p: 2,
                    borderRadius: '12px',
                    background: theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%)'
                      : 'rgba(255,255,255,0.15)',
                    backdropFilter: 'blur(20px)',
                    border: theme.palette.mode === 'dark'
                      ? '1px solid rgba(34, 197, 94, 0.2)'
                      : '1px solid rgba(255,255,255,0.2)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 8px 32px rgba(34, 197, 94, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                      : 'none',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: theme.palette.mode === 'dark'
                        ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.25) 0%, rgba(16, 185, 129, 0.2) 100%)'
                        : 'rgba(255,255,255,0.25)',
                      transform: 'translateY(-2px)',
                      boxShadow: theme.palette.mode === 'dark'
                        ? '0 12px 40px rgba(34, 197, 94, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                        : '0 4px 20px rgba(0,0,0,0.1)',
                    }
                  }}
                >
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <DollarSign size={20} color="rgba(255,255,255,0.8)" />
                    <Typography variant="body2" color="rgba(255,255,255,0.9)" fontWeight="500">
                      Total Value Created
                    </Typography>
                  </Box>
                  <Typography 
                    variant="h5" 
                    fontWeight="bold" 
                    color={totalValue - metrics['Total Contributions'] >= 0 ? '#4ade80' : '#f87171'}
                    sx={{ textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}
                  >
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD',
                      minimumFractionDigits: 0,
                      notation: 'compact',
                      compactDisplay: 'short'
                    }).format(totalValue - metrics['Total Contributions'])}
                  </Typography>
                  <Typography variant="caption" color="rgba(255,255,255,0.7)">
                    Net value generation above capital
                  </Typography>
                </Box>

                {/* Investment Status */}
                <Box 
                  sx={{ 
                    p: 2,
                    borderRadius: '12px',
                    background: theme.palette.mode === 'dark'
                      ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)'
                      : 'rgba(255,255,255,0.15)',
                    backdropFilter: 'blur(20px)',
                    border: theme.palette.mode === 'dark'
                      ? '1px solid rgba(139, 92, 246, 0.2)'
                      : '1px solid rgba(255,255,255,0.2)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 8px 32px rgba(139, 92, 246, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                      : 'none',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: theme.palette.mode === 'dark'
                        ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(168, 85, 247, 0.2) 100%)'
                        : 'rgba(255,255,255,0.25)',
                      transform: 'translateY(-2px)',
                      boxShadow: theme.palette.mode === 'dark'
                        ? '0 12px 40px rgba(139, 92, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                        : '0 4px 20px rgba(0,0,0,0.1)',
                    }
                  }}
                >
                                     <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box display="flex" alignItems="center" gap={2}>
                      <PieChart size={20} color="rgba(255,255,255,0.8)" />
                      <Typography variant="body2" color="rgba(255,255,255,0.9)" fontWeight="500">
                        Investment Status
                      </Typography>
                    </Box>
                    <Chip
                      label={metrics['Final NAV'] > 0 ? "Active" : "Fully Liquidated"}
                      sx={{
                        backgroundColor: metrics['Final NAV'] > 0 ? 'rgba(59, 130, 246, 0.8)' : 'rgba(107, 114, 128, 0.8)',
                        color: 'white',
                        fontWeight: 'bold',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        '& .MuiChip-label': {
                          padding: '8px 16px',
                        }
                      }}
                    />
                  </Box>
                  <Typography variant="caption" color="rgba(255,255,255,0.7)" sx={{ mt: 1, display: 'block' }}>
                    {metrics['Final NAV'] > 0 ? 'Portfolio actively managed' : 'Investment cycle complete'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Benchmark Comparison (if available) */}
      {data.has_benchmark && (
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" mb={3}>
              Benchmark Comparison
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Benchmark analysis feature coming soon...
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Enhanced Investment Insights */}
      <Card sx={{ 
        background: theme.palette.mode === 'dark' 
          ? '#000000'
          : 'background.paper',
        border: theme.palette.mode === 'dark' 
          ? '1px solid rgba(255,255,255,0.1)'
          : '1px solid',
        borderColor: theme.palette.mode === 'dark' 
          ? 'rgba(255,255,255,0.1)'
          : 'divider',
        position: 'relative',
        overflow: 'hidden',
        '&::before': theme.palette.mode === 'dark' ? {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 15% 25%, rgba(34, 197, 94, 0.05) 0%, transparent 50%), radial-gradient(circle at 85% 75%, rgba(59, 130, 246, 0.05) 0%, transparent 50%)',
          backdropFilter: 'blur(10px)',
        } : {}
      }}>
        <CardContent sx={{ p: 2.5, position: 'relative', zIndex: 1 }}>
          <Box display="flex" alignItems="center" gap={1.5} mb={2.5}>
            <Box 
              sx={{ 
                p: 1, 
                borderRadius: '10px', 
                backgroundColor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <TrendingUp size={20} color="white" />
            </Box>
            <Typography variant="h6" fontWeight="bold">
              Investment Insights & Analysis
            </Typography>
          </Box>

          <Box display="grid" gridTemplateColumns={{ xs: '1fr', md: 'repeat(2, 1fr)' }} gap={2.5}>
            {/* Performance Assessment Card */}
            <Paper 
              sx={{ 
                p: 2,
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%)'
                  : 'background.default',
                border: 1,
                borderColor: theme.palette.mode === 'dark' 
                  ? 'rgba(34, 197, 94, 0.2)'
                  : 'divider',
                boxShadow: theme.palette.mode === 'dark'
                  ? '0 8px 32px rgba(34, 197, 94, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                  : 'none',
                '&:hover': { 
                  transform: 'translateY(-2px)', 
                  transition: 'all 0.3s ease',
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 12px 40px rgba(34, 197, 94, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                    : '0 4px 20px rgba(0,0,0,0.1)',
                }
              }}
            >
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Box 
                  sx={{ 
                    p: 1, 
                    borderRadius: '8px', 
                    backgroundColor: performance.color + '20',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                >
                  {performance.trend === 'up' ? <TrendingUp size={20} color={performance.color} /> : 
                   performance.trend === 'down' ? <Target size={20} color={performance.color} /> :
                   <DollarSign size={20} color={performance.color} />}
                </Box>
                <Typography variant="h6" fontWeight="bold">
                  Performance Assessment
                </Typography>
                <Chip 
                  label={performance.label}
                  size="small"
                  sx={{ 
                    backgroundColor: performance.color + '20',
                    color: performance.color,
                    fontWeight: 'bold',
                    ml: 'auto'
                  }}
                />
              </Box>
              
              <Typography variant="body1" mb={2} lineHeight={1.6}>
                {metrics['TVPI'] > 1.5 && metrics['Fund IRR'] > 0.15 
                  ? "Outstanding investment performance with exceptional returns. The fund has significantly outperformed typical private equity benchmarks."
                  : metrics['TVPI'] > 1.2 && metrics['Fund IRR'] > 0.10
                  ? "Strong investment performance demonstrating solid value creation and competitive returns relative to market expectations."
                  : metrics['TVPI'] > 1.0
                  ? "Moderate performance with positive returns, though below typical private equity return expectations. Consider reviewing investment strategy."
                  : "Performance below expectations requiring immediate strategic review. Risk factors may need to be reassessed."
                }
              </Typography>

              <Box display="flex" gap={2} flexWrap="wrap">
                <Chip
                  label={`IRR: ${(metrics['Fund IRR'] * 100).toFixed(1)}%`}
                  size="small"
                  variant="outlined"
                  sx={{ borderColor: performance.color, color: performance.color }}
                />
                <Chip
                  label={`Multiple: ${metrics['TVPI'].toFixed(2)}x`}
                  size="small"
                  variant="outlined"
                  sx={{ borderColor: performance.color, color: performance.color }}
                />
              </Box>
            </Paper>

            {/* Liquidity Status Card */}
            <Paper 
              sx={{ 
                p: 2,
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%)'
                  : 'background.default',
                border: 1,
                borderColor: theme.palette.mode === 'dark' 
                  ? 'rgba(59, 130, 246, 0.2)'
                  : 'divider',
                boxShadow: theme.palette.mode === 'dark'
                  ? '0 8px 32px rgba(59, 130, 246, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                  : 'none',
                '&:hover': { 
                  transform: 'translateY(-2px)', 
                  transition: 'all 0.3s ease',
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 12px 40px rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                    : '0 4px 20px rgba(0,0,0,0.1)',
                }
              }}
            >
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Box 
                  sx={{ 
                    p: 1, 
                    borderRadius: '8px', 
                    backgroundColor: 'info.main',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                >
                  <PieChart size={20} color="white" />
                </Box>
                <Typography variant="h6" fontWeight="bold">
                  Liquidity Analysis
                </Typography>
                <Chip 
                  label={`${(realizationRate * 100).toFixed(1)}% Realized`}
                  size="small"
                  sx={{ 
                    backgroundColor: 'info.main',
                    color: 'white',
                    fontWeight: 'bold',
                    ml: 'auto'
                  }}
                />
              </Box>
              
              <Typography variant="body1" mb={2} lineHeight={1.6}>
                {realizationRate > 0.8
                  ? "Excellent liquidity profile with most capital already returned to investors. Remaining NAV represents bonus upside potential."
                  : realizationRate > 0.5
                  ? "Balanced liquidity position with meaningful cash distributions already received while maintaining significant remaining value potential."
                  : "Early-stage liquidity profile with substantial unrealized value. Focus should be on portfolio company development and exit planning."
                }
              </Typography>

              <Box display="flex" gap={2} flexWrap="wrap">
                <Chip
                  label={`DPI: ${metrics['DPI'].toFixed(2)}x`}
                  size="small"
                  variant="outlined"
                  sx={{ borderColor: 'success.main', color: 'success.main' }}
                />
                <Chip
                  label={`RVPI: ${metrics['RVPI'].toFixed(2)}x`}
                  size="small"
                  variant="outlined"
                  sx={{ borderColor: 'primary.main', color: 'primary.main' }}
                />
              </Box>
            </Paper>
          </Box>

          {/* Additional Strategic Insights */}
          <Box mt={2.5}>
            <Typography variant="subtitle1" fontWeight="bold" mb={2}>
              Strategic Recommendations
            </Typography>
            <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={2}>
              
              {/* Investment Timing Insight */}
              <Paper 
                sx={{ 
                  p: 2, 
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%)'
                    : 'background.default',
                  border: 1,
                  borderColor: theme.palette.mode === 'dark' 
                    ? 'rgba(245, 158, 11, 0.2)'
                    : 'warning.main',
                  borderRadius: 2,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 32px rgba(245, 158, 11, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                    : 'none',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 12px 40px rgba(245, 158, 11, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                      : '0 4px 20px rgba(0,0,0,0.1)',
                  }
                }}
              >
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Target size={20} color={theme.palette.mode === 'dark' ? '#f59e0b' : 'orange'} />
                  <Typography variant="subtitle2" fontWeight="bold" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.9)' : 'warning.main'}>
                    Investment Timing
                  </Typography>
                </Box>
                <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'}>
                  {metrics['TVPI'] > 1.3 
                    ? "Well-timed investment showing strong value creation in current market cycle."
                    : "Consider market timing factors and portfolio diversification for future investments."
                  }
                </Typography>
              </Paper>

              {/* Risk Assessment */}
              <Paper 
                sx={{ 
                  p: 2, 
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%)'
                    : 'background.default',
                  border: 1,
                  borderColor: theme.palette.mode === 'dark' 
                    ? 'rgba(59, 130, 246, 0.2)'
                    : 'primary.main',
                  borderRadius: 2,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 32px rgba(59, 130, 246, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                    : 'none',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 12px 40px rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                      : '0 4px 20px rgba(0,0,0,0.1)',
                  }
                }}
              >
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <DollarSign size={20} color={theme.palette.mode === 'dark' ? '#3b82f6' : 'blue'} />
                  <Typography variant="subtitle2" fontWeight="bold" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.9)' : 'primary.main'}>
                    Risk Profile
                  </Typography>
                </Box>
                <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'}>
                  {realizationRate > 0.6 
                    ? "Risk significantly reduced with substantial capital already returned."
                    : "Monitor remaining portfolio concentration and diversification needs."
                  }
                </Typography>
              </Paper>

              {/* Future Outlook */}
              <Paper 
                sx={{ 
                  p: 2, 
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%)'
                    : 'background.default',
                  border: 1,
                  borderColor: theme.palette.mode === 'dark' 
                    ? 'rgba(34, 197, 94, 0.2)'
                    : 'success.main',
                  borderRadius: 2,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 32px rgba(34, 197, 94, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                    : 'none',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 12px 40px rgba(34, 197, 94, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                      : '0 4px 20px rgba(0,0,0,0.1)',
                  }
                }}
              >
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <TrendingUp size={20} color={theme.palette.mode === 'dark' ? '#22c55e' : 'green'} />
                  <Typography variant="subtitle2" fontWeight="bold" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.9)' : 'success.main'}>
                    Outlook
                  </Typography>
                </Box>
                <Typography variant="body2" color={theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'}>
                  {metrics['RVPI'] > 0.5 
                    ? "Significant upside potential remains with strong remaining NAV position."
                    : "Focus on optimizing remaining portfolio value and exit timing."
                  }
                </Typography>
              </Paper>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}; 