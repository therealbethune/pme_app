import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  formatAsPercent?: boolean;
  formatAsMultiple?: boolean;
  formatAsCurrency?: boolean;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  benchmark?: number;
  description?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  formatAsPercent = false,
  formatAsMultiple = false,
  formatAsCurrency = false,
  icon,
  trend,
  benchmark,
  description
}) => {
  const formatValue = (val: number | string): string => {
    if (typeof val === 'string') return val;
    
    if (formatAsPercent) {
      return `${(val * 100).toFixed(1)}%`;
    }
    if (formatAsMultiple) {
      return `${val.toFixed(2)}x`;
    }
    if (formatAsCurrency) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(val);
    }
    return typeof val === 'number' ? val.toFixed(2) : val;
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp size={16} color="#22c55e" />;
      case 'down': return <TrendingDown size={16} color="#ef4444" />;
      case 'neutral': return <Minus size={16} color="#6b7280" />;
      default: return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up': return '#22c55e';
      case 'down': return '#ef4444';
      case 'neutral': return '#6b7280';
      default: return 'inherit';
    }
  };

  return (
    <Card 
      sx={{ 
        height: '100%', 
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
        border: trend ? `2px solid ${getTrendColor()}20` : '1px solid #e5e7eb'
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {icon}
            <Typography variant="body2" color="text.secondary" fontWeight={500}>
              {title}
            </Typography>
          </Box>
          {getTrendIcon()}
        </Box>
        
        <Typography 
          variant="h4" 
          component="div" 
          fontWeight="bold"
          color={trend ? getTrendColor() : 'text.primary'}
          mb={1}
        >
          {formatValue(value)}
        </Typography>

        {subtitle && (
          <Typography variant="body2" color="text.secondary" mb={1}>
            {subtitle}
          </Typography>
        )}

        {benchmark && typeof value === 'number' && (
          <Box mt={1}>
            <Chip
              label={`vs. Benchmark: ${formatValue(value - benchmark)}`}
              size="small"
              color={value > benchmark ? 'success' : value < benchmark ? 'error' : 'default'}
              sx={{ fontSize: '0.75rem' }}
            />
          </Box>
        )}

        {description && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}; 