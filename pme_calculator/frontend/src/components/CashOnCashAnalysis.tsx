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
  useTheme
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  Timeline,
  ExpandMore,
  MonetizationOn,
  ShowChart
} from '@mui/icons-material';

interface CashOnCashData {
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
}

interface CashOnCashAnalysisProps {
  data: CashOnCashData;
}

const CashOnCashAnalysis: React.FC<CashOnCashAnalysisProps> = ({ data }) => {
  const theme = useTheme();

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'excellent': return theme.palette.success.main;
      case 'good': return theme.palette.success.light;
      case 'moderate': return theme.palette.warning.main;
      case 'underperforming': return theme.palette.error.main;
      case 'high': return theme.palette.success.main;
      case 'low': return theme.palette.error.main;
      case 'steady': return theme.palette.success.main;
      case 'lumpy': return theme.palette.warning.main;
      default: return theme.palette.primary.main;
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

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatMultiple = (value: number) => {
    return `${value.toFixed(2)}x`;
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
          Cash-on-Cash Return Analysis
        </Typography>
      </Box>

      {/* Overall Metrics Cards */}
      <Box 
        display="grid" 
        gridTemplateColumns={{ 
          xs: 'repeat(2, 1fr)', 
          md: 'repeat(4, 1fr)' 
        }} 
        gap={3} 
        sx={{ mb: 3 }}
      >
        <Paper 
          sx={{ 
            p: 2, 
            textAlign: 'center',
            backgroundColor: theme.palette.background.default,
            border: `1px solid ${theme.palette.divider}`
          }}
        >
          <TrendingUp sx={{ color: theme.palette.primary.main, mb: 1 }} />
          <Typography variant="h4" fontWeight="700" color="text.primary">
            {formatMultiple(data.overall_metrics.total_cash_on_cash_return)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total Cash-on-Cash Return
          </Typography>
        </Paper>

        <Paper 
          sx={{ 
            p: 2, 
            textAlign: 'center',
            backgroundColor: theme.palette.background.default,
            border: `1px solid ${theme.palette.divider}`
          }}
        >
          <AccountBalance sx={{ color: theme.palette.success.main, mb: 1 }} />
          <Typography variant="h4" fontWeight="700" color="text.primary">
            {formatPercentage(data.overall_metrics.cash_yield)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Cash Yield
          </Typography>
        </Paper>

        <Paper 
          sx={{ 
            p: 2, 
            textAlign: 'center',
            backgroundColor: theme.palette.background.default,
            border: `1px solid ${theme.palette.divider}`
          }}
        >
          <ShowChart sx={{ color: theme.palette.warning.main, mb: 1 }} />
          <Typography variant="h4" fontWeight="700" color="text.primary">
            {formatPercentage(data.overall_metrics.unrealized_return)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Unrealized Return
          </Typography>
        </Paper>

        <Paper 
          sx={{ 
            p: 2, 
            textAlign: 'center',
            backgroundColor: theme.palette.background.default,
            border: `1px solid ${theme.palette.divider}`
          }}
        >
          <Timeline sx={{ color: theme.palette.info.main, mb: 1 }} />
          <Typography variant="h4" fontWeight="700" color="text.primary">
            {data.overall_metrics.fund_life_years.toFixed(1)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Fund Life (Years)
          </Typography>
        </Paper>
      </Box>

      {/* Performance Insights */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" fontWeight="600" color="text.primary" sx={{ mb: 2 }}>
          Performance Insights
        </Typography>
        <Box 
          display="grid" 
          gridTemplateColumns={{ 
            xs: '1fr', 
            sm: 'repeat(3, 1fr)' 
          }} 
          gap={2}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Performance Status:
            </Typography>
            <Chip 
              label={data.insights.performance_status}
              sx={{ 
                backgroundColor: getStatusColor(data.insights.performance_status),
                color: 'white',
                fontWeight: '600'
              }}
              size="small"
            />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Cash Efficiency:
            </Typography>
            <Chip 
              label={data.insights.cash_efficiency}
              sx={{ 
                backgroundColor: getStatusColor(data.insights.cash_efficiency),
                color: 'white',
                fontWeight: '600'
              }}
              size="small"
            />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Distribution Pattern:
            </Typography>
            <Chip 
              label={data.insights.distribution_pattern}
              sx={{ 
                backgroundColor: getStatusColor(data.insights.distribution_pattern),
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
        <Box sx={{ mb: 3 }}>
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

      {/* Quarterly Breakdown */}
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
            Quarterly Cash Flow Analysis
          </Typography>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0 }}>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ backgroundColor: theme.palette.background.default }}>
                  <TableCell><strong>Quarter</strong></TableCell>
                  <TableCell align="right"><strong>Contributions</strong></TableCell>
                  <TableCell align="right"><strong>Distributions</strong></TableCell>
                  <TableCell align="right"><strong>NAV</strong></TableCell>
                  <TableCell align="right"><strong>CoC Return</strong></TableCell>
                  <TableCell align="right"><strong>Cash Returned</strong></TableCell>
                  <TableCell align="right"><strong>Unrealized</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.quarterly_breakdown.map((quarter, index) => (
                  <TableRow 
                    key={index}
                    sx={{ 
                      '&:nth-of-type(odd)': { 
                        backgroundColor: theme.palette.action.hover 
                      },
                      '&:hover': {
                        backgroundColor: theme.palette.action.selected
                      }
                    }}
                  >
                    <TableCell component="th" scope="row">
                      <strong>{quarter.quarter}</strong>
                    </TableCell>
                    <TableCell align="right">
                      {quarter.contributions > 0 ? formatCurrency(quarter.contributions) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {quarter.distributions > 0 ? formatCurrency(quarter.distributions) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(quarter.nav)}
                    </TableCell>
                    <TableCell align="right">
                      <strong>{formatMultiple(quarter.cash_on_cash_return)}</strong>
                    </TableCell>
                    <TableCell align="right">
                      {formatPercentage(quarter.cash_returned_ratio)}
                    </TableCell>
                    <TableCell align="right">
                      {formatPercentage(quarter.unrealized_ratio)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default CashOnCashAnalysis; 