import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, FormControl, InputLabel, Select, MenuItem,
  Slider, TextField, Switch, FormControlLabel, Chip, Divider,
  Accordion, AccordionSummary, AccordionDetails, Button, ButtonGroup,
  Grid, Paper, Stack
} from '@mui/material';
import { ExpandMore, FilterAlt, Refresh, Download } from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface FilterCriteria {
  dateRange: {
    start: string;
    end: string;
  };
  performanceMetrics: {
    irrRange: [number, number];
    tvpiRange: [number, number];
    dpiRange: [number, number];
  };
  cashFlowFilters: {
    minCashFlow: number;
    maxCashFlow: number;
    flowType: 'all' | 'contributions' | 'distributions';
  };
  benchmarkComparison: {
    enabled: boolean;
    showOutperformance: boolean;
    showUnderperformance: boolean;
  };
  analysisType: 'basic' | 'advanced' | 'institutional';
  quarterFilters: string[];
}

interface InteractiveFiltersProps {
  onFilterChange: (filters: FilterCriteria) => void;
  availableQuarters: string[];
  currentMetrics?: {
    irr: { min: number; max: number; current: number };
    tvpi: { min: number; max: number; current: number };
    dpi: { min: number; max: number; current: number };
  };
  hasBenchmark: boolean;
}

export const InteractiveFilters: React.FC<InteractiveFiltersProps> = ({
  onFilterChange,
  availableQuarters,
  currentMetrics,
  hasBenchmark
}) => {
  const theme = useTheme();
  const [filters, setFilters] = useState<FilterCriteria>({
    dateRange: {
      start: '',
      end: ''
    },
    performanceMetrics: {
      irrRange: [currentMetrics?.irr.min || -0.5, currentMetrics?.irr.max || 0.5],
      tvpiRange: [currentMetrics?.tvpi.min || 0, currentMetrics?.tvpi.max || 5],
      dpiRange: [currentMetrics?.dpi.min || 0, currentMetrics?.dpi.max || 5]
    },
    cashFlowFilters: {
      minCashFlow: -10000000,
      maxCashFlow: 10000000,
      flowType: 'all'
    },
    benchmarkComparison: {
      enabled: hasBenchmark,
      showOutperformance: true,
      showUnderperformance: true
    },
    analysisType: 'advanced',
    quarterFilters: []
  });

  const handleFilterUpdate = (newFilters: Partial<FilterCriteria>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    onFilterChange(updatedFilters);
  };

  const resetFilters = () => {
    const defaultFilters: FilterCriteria = {
      dateRange: { start: '', end: '' },
      performanceMetrics: {
        irrRange: [currentMetrics?.irr.min || -0.5, currentMetrics?.irr.max || 0.5],
        tvpiRange: [currentMetrics?.tvpi.min || 0, currentMetrics?.tvpi.max || 5],
        dpiRange: [currentMetrics?.dpi.min || 0, currentMetrics?.dpi.max || 5]
      },
      cashFlowFilters: {
        minCashFlow: -10000000,
        maxCashFlow: 10000000,
        flowType: 'all'
      },
      benchmarkComparison: {
        enabled: hasBenchmark,
        showOutperformance: true,
        showUnderperformance: true
      },
      analysisType: 'advanced',
      quarterFilters: []
    };
    setFilters(defaultFilters);
    onFilterChange(defaultFilters);
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.dateRange.start || filters.dateRange.end) count++;
    if (filters.quarterFilters.length > 0) count++;
    if (filters.cashFlowFilters.flowType !== 'all') count++;
    if (!filters.benchmarkComparison.enabled && hasBenchmark) count++;
    return count;
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box display="flex" alignItems="center" gap={2}>
            <FilterAlt />
            <Typography variant="h6" fontWeight="bold">
              Interactive Analysis Filters
            </Typography>
            {getActiveFilterCount() > 0 && (
              <Chip 
                label={`${getActiveFilterCount()} active`}
                size="small" 
                color="primary"
              />
            )}
          </Box>
          <Box display="flex" gap={1}>
            <Button
              startIcon={<Refresh />}
              onClick={resetFilters}
              variant="outlined"
              size="small"
            >
              Reset
            </Button>
            <Button
              startIcon={<Download />}
              variant="contained"
              size="small"
            >
              Export
            </Button>
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Analysis Type Selection */}
        <Box mb={3}>
          <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
            Analysis Type
          </Typography>
          <ButtonGroup variant="outlined" sx={{ mb: 2 }}>
            <Button
              variant={filters.analysisType === 'basic' ? 'contained' : 'outlined'}
              onClick={() => handleFilterUpdate({ analysisType: 'basic' })}
            >
              Basic
            </Button>
            <Button
              variant={filters.analysisType === 'advanced' ? 'contained' : 'outlined'}
              onClick={() => handleFilterUpdate({ analysisType: 'advanced' })}
            >
              Advanced
            </Button>
            <Button
              variant={filters.analysisType === 'institutional' ? 'contained' : 'outlined'}
              onClick={() => handleFilterUpdate({ analysisType: 'institutional' })}
            >
              Institutional
            </Button>
          </ButtonGroup>
        </Box>

        {/* Date Range Filters */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1" fontWeight="medium">
              Time Period Filters
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Start Date"
                  type="date"
                  value={filters.dateRange.start}
                  onChange={(e) => 
                    handleFilterUpdate({ 
                      dateRange: { ...filters.dateRange, start: e.target.value } 
                    })
                  }
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="End Date"
                  type="date"
                  value={filters.dateRange.end}
                  onChange={(e) => 
                    handleFilterUpdate({ 
                      dateRange: { ...filters.dateRange, end: e.target.value } 
                    })
                  }
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>

            {/* Quarter Selection */}
            <Box mt={3}>
              <Typography variant="body2" fontWeight="medium" gutterBottom>
                Select Specific Quarters
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {availableQuarters.map((quarter) => (
                  <Chip
                    key={quarter}
                    label={quarter}
                    variant={filters.quarterFilters.includes(quarter) ? 'filled' : 'outlined'}
                    onClick={() => {
                      const newFilters = filters.quarterFilters.includes(quarter)
                        ? filters.quarterFilters.filter(q => q !== quarter)
                        : [...filters.quarterFilters, quarter];
                      handleFilterUpdate({ quarterFilters: newFilters });
                    }}
                    clickable
                  />
                ))}
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Performance Metrics Filters */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1" fontWeight="medium">
              Performance Metrics
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={3}>
              {/* IRR Range */}
              <Box>
                <Typography variant="body2" fontWeight="medium" gutterBottom>
                  IRR Range ({(filters.performanceMetrics.irrRange[0] * 100).toFixed(1)}% - {(filters.performanceMetrics.irrRange[1] * 100).toFixed(1)}%)
                </Typography>
                <Slider
                  value={filters.performanceMetrics.irrRange}
                  onChange={(_, value) => 
                    handleFilterUpdate({
                      performanceMetrics: {
                        ...filters.performanceMetrics,
                        irrRange: value as [number, number]
                      }
                    })
                  }
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(1)}%`}
                  min={-0.5}
                  max={1.0}
                  step={0.01}
                />
              </Box>

              {/* TVPI Range */}
              <Box>
                <Typography variant="body2" fontWeight="medium" gutterBottom>
                  TVPI Range ({filters.performanceMetrics.tvpiRange[0].toFixed(2)}x - {filters.performanceMetrics.tvpiRange[1].toFixed(2)}x)
                </Typography>
                <Slider
                  value={filters.performanceMetrics.tvpiRange}
                  onChange={(_, value) => 
                    handleFilterUpdate({
                      performanceMetrics: {
                        ...filters.performanceMetrics,
                        tvpiRange: value as [number, number]
                      }
                    })
                  }
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${value.toFixed(2)}x`}
                  min={0}
                  max={10}
                  step={0.1}
                />
              </Box>

              {/* DPI Range */}
              <Box>
                <Typography variant="body2" fontWeight="medium" gutterBottom>
                  DPI Range ({filters.performanceMetrics.dpiRange[0].toFixed(2)}x - {filters.performanceMetrics.dpiRange[1].toFixed(2)}x)
                </Typography>
                <Slider
                  value={filters.performanceMetrics.dpiRange}
                  onChange={(_, value) => 
                    handleFilterUpdate({
                      performanceMetrics: {
                        ...filters.performanceMetrics,
                        dpiRange: value as [number, number]
                      }
                    })
                  }
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${value.toFixed(2)}x`}
                  min={0}
                  max={10}
                  step={0.1}
                />
              </Box>
            </Stack>
          </AccordionDetails>
        </Accordion>

        {/* Cash Flow Filters */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1" fontWeight="medium">
              Cash Flow Analysis
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={3}>
              <FormControl fullWidth>
                <InputLabel>Cash Flow Type</InputLabel>
                <Select
                  value={filters.cashFlowFilters.flowType}
                  label="Cash Flow Type"
                  onChange={(e) => 
                    handleFilterUpdate({
                      cashFlowFilters: {
                        ...filters.cashFlowFilters,
                        flowType: e.target.value as 'all' | 'contributions' | 'distributions'
                      }
                    })
                  }
                >
                  <MenuItem value="all">All Cash Flows</MenuItem>
                  <MenuItem value="contributions">Contributions Only</MenuItem>
                  <MenuItem value="distributions">Distributions Only</MenuItem>
                </Select>
              </FormControl>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="Min Cash Flow ($M)"
                    type="number"
                    value={filters.cashFlowFilters.minCashFlow / 1000000}
                    onChange={(e) => 
                      handleFilterUpdate({
                        cashFlowFilters: {
                          ...filters.cashFlowFilters,
                          minCashFlow: Number(e.target.value) * 1000000
                        }
                      })
                    }
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Max Cash Flow ($M)"
                    type="number"
                    value={filters.cashFlowFilters.maxCashFlow / 1000000}
                    onChange={(e) => 
                      handleFilterUpdate({
                        cashFlowFilters: {
                          ...filters.cashFlowFilters,
                          maxCashFlow: Number(e.target.value) * 1000000
                        }
                      })
                    }
                    fullWidth
                  />
                </Grid>
              </Grid>
            </Stack>
          </AccordionDetails>
        </Accordion>

        {/* Benchmark Comparison */}
        {hasBenchmark && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1" fontWeight="medium">
                Benchmark Comparison
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Stack spacing={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={filters.benchmarkComparison.enabled}
                      onChange={(e) => 
                        handleFilterUpdate({
                          benchmarkComparison: {
                            ...filters.benchmarkComparison,
                            enabled: e.target.checked
                          }
                        })
                      }
                    />
                  }
                  label="Enable Benchmark Analysis"
                />
                
                {filters.benchmarkComparison.enabled && (
                  <>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={filters.benchmarkComparison.showOutperformance}
                          onChange={(e) => 
                            handleFilterUpdate({
                              benchmarkComparison: {
                                ...filters.benchmarkComparison,
                                showOutperformance: e.target.checked
                              }
                            })
                          }
                        />
                      }
                      label="Show Outperformance Periods"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={filters.benchmarkComparison.showUnderperformance}
                          onChange={(e) => 
                            handleFilterUpdate({
                              benchmarkComparison: {
                                ...filters.benchmarkComparison,
                                showUnderperformance: e.target.checked
                              }
                            })
                          }
                        />
                      }
                      label="Show Underperformance Periods"
                    />
                  </>
                )}
              </Stack>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Active Filters Summary */}
        {getActiveFilterCount() > 0 && (
          <Paper sx={{ p: 2, mt: 3, bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50' }}>
            <Typography variant="subtitle2" fontWeight="medium" gutterBottom>
              Active Filters Summary
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {filters.dateRange.start && (
                <Chip label={`From: ${filters.dateRange.start}`} size="small" />
              )}
              {filters.dateRange.end && (
                <Chip label={`To: ${filters.dateRange.end}`} size="small" />
              )}
              {filters.quarterFilters.length > 0 && (
                <Chip label={`${filters.quarterFilters.length} quarters selected`} size="small" />
              )}
              {filters.cashFlowFilters.flowType !== 'all' && (
                <Chip label={`Cash Flow: ${filters.cashFlowFilters.flowType}`} size="small" />
              )}
              <Chip label={`Analysis: ${filters.analysisType}`} size="small" />
            </Box>
          </Paper>
        )}
      </CardContent>
    </Card>
  );
};

export default InteractiveFilters; 