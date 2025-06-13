import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  ExpandMore,
  MonetizationOn,
  CallMade,
  CallReceived,
  FlashOn
} from '@mui/icons-material';

interface CashFlowData {
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
}

interface CashFlowAnalysisProps {
  data: CashFlowData;
}

const CashFlowAnalysis: React.FC<CashFlowAnalysisProps> = ({ data }) => {
  const theme = useTheme();

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'excellent': case 'fast': case 'very consistent': case 'fast recovery':
        return theme.palette.success.main;
      case 'good': case 'moderate': case 'consistent': case 'normal recovery':
        return theme.palette.primary.main;
      case 'developing': case 'slow': case 'irregular': case 'slow recovery':
        return theme.palette.warning.main;
      case 'still negative': case 'no distributions':
        return theme.palette.error.main;
      default: return theme.palette.text.secondary;
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value: number, decimals = 1) => {
    return value.toFixed(decimals);
  };

  const getVelocityDescription = (velocity: number) => {
    if (velocity > 5000000) return 'High velocity capital movement';
    if (velocity > 2000000) return 'Moderate velocity capital movement';
    return 'Conservative velocity capital movement';
  };

  const getJCurveProgress = () => {
    if (!data.j_curve_analysis.time_to_positive_years) return 0;
    const recovery = data.j_curve_analysis.j_curve_recovery;
    const depth = Math.abs(data.j_curve_analysis.j_curve_depth);
    return Math.min(100, (recovery / depth) * 100);
  };

  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 3, 
        mt: 3,
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`
      }}
    >
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <MonetizationOn sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
        <Typography variant="h5" fontWeight="600" color="text.primary">
          Cash Flow Analysis
        </Typography>
      </Box>

      {/* Velocity Metrics */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight="600" color="text.primary" sx={{ mb: 2 }}>
          Cash Flow Velocity
        </Typography>
        <Box 
          display="grid" 
          gridTemplateColumns={{ xs: '1fr', md: 'repeat(3, 1fr)' }} 
          gap={3}
        >
          <Paper 
            sx={{ 
              p: 3, 
              textAlign: 'center',
              backgroundColor: theme.palette.background.default,
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            <CallReceived sx={{ color: theme.palette.error.main, mb: 1, fontSize: 32 }} />
            <Typography variant="h4" fontWeight="700" color="text.primary">
              {formatCurrency(data.velocity_metrics.deployment_velocity)}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Deployment Velocity (Annual)
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {getVelocityDescription(data.velocity_metrics.deployment_velocity)}
            </Typography>
          </Paper>

          <Paper 
            sx={{ 
              p: 3, 
              textAlign: 'center',
              backgroundColor: theme.palette.background.default,
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            <CallMade sx={{ color: theme.palette.success.main, mb: 1, fontSize: 32 }} />
            <Typography variant="h4" fontWeight="700" color="text.primary">
              {formatCurrency(data.velocity_metrics.distribution_velocity)}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Distribution Velocity (Annual)
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {getVelocityDescription(data.velocity_metrics.distribution_velocity)}
            </Typography>
          </Paper>

          <Paper 
            sx={{ 
              p: 3, 
              textAlign: 'center',
              backgroundColor: theme.palette.background.default,
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            <FlashOn sx={{ color: theme.palette.warning.main, mb: 1, fontSize: 32 }} />
            <Typography variant="h4" fontWeight="700" color="text.primary">
              {formatCurrency(data.velocity_metrics.net_cash_flow_velocity)}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Net Cash Flow Velocity (Annual)
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Overall net cash generation rate
            </Typography>
          </Paper>
        </Box>
      </Box>

      {/* J-Curve Analysis */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight="600" color="text.primary" sx={{ mb: 2 }}>
          J-Curve Analysis
        </Typography>
        <Paper 
          sx={{ 
            p: 3,
            backgroundColor: theme.palette.background.default,
            border: `1px solid ${theme.palette.divider}`
          }}
        >
          <Box 
            display="grid" 
            gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} 
            gap={3}
            sx={{ mb: 3 }}
          >
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="700" color="text.primary">
                {formatCurrency(data.j_curve_analysis.j_curve_depth)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                J-Curve Depth
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="700" color="text.primary">
                {formatNumber(data.j_curve_analysis.time_to_bottom_years)} years
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Time to Bottom
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="700" color="text.primary">
                {data.j_curve_analysis.time_to_positive_years 
                  ? `${formatNumber(data.j_curve_analysis.time_to_positive_years)} years`
                  : 'N/A'
                }
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Time to Positive
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="h5" fontWeight="700" color="text.primary">
                {formatCurrency(data.j_curve_analysis.current_cumulative_cash)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Current Net Position
              </Typography>
            </Box>
          </Box>

          {/* J-Curve Progress Bar */}
          <Box sx={{ mb: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                J-Curve Recovery Progress
              </Typography>
              <Chip 
                label={data.insights.j_curve_status}
                sx={{ 
                  backgroundColor: getStatusColor(data.insights.j_curve_status),
                  color: 'white',
                  fontWeight: '600'
                }}
                size="small"
              />
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={getJCurveProgress()} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                backgroundColor: theme.palette.action.hover,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getStatusColor(data.insights.j_curve_status)
                }
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {getJCurveProgress().toFixed(1)}% recovery from bottom
            </Typography>
          </Box>
        </Paper>
      </Box>

      {/* Cash Flow Health Indicators */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight="600" color="text.primary" sx={{ mb: 2 }}>
          Cash Flow Health Indicators
        </Typography>
        <Box 
          display="grid" 
          gridTemplateColumns={{ xs: '1fr', sm: 'repeat(3, 1fr)' }} 
          gap={2}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Velocity Assessment:
            </Typography>
            <Chip 
              label={data.insights.velocity_assessment}
              sx={{ 
                backgroundColor: getStatusColor(data.insights.velocity_assessment),
                color: 'white',
                fontWeight: '600'
              }}
              size="small"
            />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              J-Curve Status:
            </Typography>
            <Chip 
              label={data.insights.j_curve_status}
              sx={{ 
                backgroundColor: getStatusColor(data.insights.j_curve_status),
                color: 'white',
                fontWeight: '600'
              }}
              size="small"
            />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Cash Flow Health:
            </Typography>
            <Chip 
              label={data.insights.cash_flow_health}
              sx={{ 
                backgroundColor: getStatusColor(data.insights.cash_flow_health),
                color: 'white',
                fontWeight: '600'
              }}
              size="small"
            />
          </Box>
        </Box>
      </Box>

      {/* Key Observations */}
      {data.insights.key_observations.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight="600" color="text.primary" sx={{ mb: 2 }}>
            Key Observations
          </Typography>
          <Box sx={{ pl: 2 }}>
            {data.insights.key_observations.map((observation, index) => (
              <Typography 
                key={index}
                variant="body2" 
                color="text.secondary"
                sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}
              >
                <Box 
                  sx={{ 
                    width: 6, 
                    height: 6, 
                    borderRadius: '50%', 
                    backgroundColor: theme.palette.primary.main 
                  }} 
                />
                {observation}
              </Typography>
            ))}
          </Box>
        </Box>
      )}

      {/* Detailed Analysis Sections */}
      <Box sx={{ mb: 3 }}>
        <Accordion sx={{ backgroundColor: theme.palette.background.paper }}>
          <AccordionSummary 
            expandIcon={<ExpandMore />}
            sx={{ 
              borderBottom: `1px solid ${theme.palette.divider}`,
              '&:hover': {
                backgroundColor: theme.palette.action.hover
              }
            }}
          >
            <Typography variant="h6" fontWeight="600" color="text.primary">
              Distribution Pattern Analysis
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 3 }}>
            <Box 
              display="grid" 
              gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)' }} 
              gap={3}
            >
              <Box>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  Distribution Events: {data.distribution_pattern.total_distribution_events}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Frequency: {formatNumber(data.distribution_pattern.distribution_frequency)} per year
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Consistency: {data.distribution_pattern.distribution_consistency}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  Average Distribution: {formatCurrency(data.distribution_pattern.average_distribution_size)}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Largest: {formatCurrency(data.distribution_pattern.largest_distribution)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Timing: {data.distribution_pattern.distribution_timing}
                </Typography>
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ backgroundColor: theme.palette.background.paper, mt: 1 }}>
          <AccordionSummary 
            expandIcon={<ExpandMore />}
            sx={{ 
              borderBottom: `1px solid ${theme.palette.divider}`,
              '&:hover': {
                backgroundColor: theme.palette.action.hover
              }
            }}
          >
            <Typography variant="h6" fontWeight="600" color="text.primary">
              Deployment Analysis
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 3 }}>
            <Box 
              display="grid" 
              gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)' }} 
              gap={3}
            >
              <Box>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  Deployment Events: {data.deployment_analysis.total_deployment_events}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Frequency: {formatNumber(data.deployment_analysis.deployment_frequency)} per year
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pattern: {data.deployment_analysis.deployment_pattern}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  Average Deployment: {formatCurrency(data.deployment_analysis.average_deployment_size)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Largest: {formatCurrency(data.deployment_analysis.largest_deployment)}
                </Typography>
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ backgroundColor: theme.palette.background.paper, mt: 1 }}>
          <AccordionSummary 
            expandIcon={<ExpandMore />}
            sx={{ 
              borderBottom: `1px solid ${theme.palette.divider}`,
              '&:hover': {
                backgroundColor: theme.palette.action.hover
              }
            }}
          >
            <Typography variant="h6" fontWeight="600" color="text.primary">
              Efficiency Metrics
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 3 }}>
            <Box 
              display="grid" 
              gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)' }} 
              gap={3}
            >
              <Box>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  Capital Efficiency: {formatNumber(data.efficiency_metrics.capital_efficiency, 2)}x
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Total value per dollar invested
                </Typography>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  Time Efficiency: {formatNumber(data.efficiency_metrics.time_efficiency, 2)}x/year
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Value generation per year
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  Cash Generation Rate: {formatCurrency(data.efficiency_metrics.cash_generation_rate)}/year
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Annual cash distributions
                </Typography>
                <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1 }}>
                  NAV Growth Rate: {formatNumber(data.efficiency_metrics.nav_growth_rate, 2)}x/year
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Annual NAV appreciation
                </Typography>
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
    </Paper>
  );
};

export default CashFlowAnalysis; 