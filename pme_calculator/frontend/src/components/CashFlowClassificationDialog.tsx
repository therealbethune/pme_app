import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import { 
  ExpandMore, 
  TrendingUp, 
  TrendingDown, 
  AccountBalance, 
  SwapVert,
  HelpOutline,
  Lightbulb
} from '@mui/icons-material';
import { useColorMode } from '../contexts/ColorModeContext';

interface UnclassifiedColumn {
  columnName: string;
  sampleValues: (number | string)[];
  detectedPatterns: string[];
  suggestedType?: string;
  confidence: number;
}

interface CashFlowClassificationDialogProps {
  open: boolean;
  onClose: () => void;
  onClassify: (classifications: { [columnName: string]: string }) => void;
  unclassifiedColumns: UnclassifiedColumn[];
  fileName: string;
}

export const CashFlowClassificationDialog: React.FC<CashFlowClassificationDialogProps> = ({
  open,
  onClose,
  onClassify,
  unclassifiedColumns,
  fileName
}) => {
  const { isDarkMode } = useColorMode();
  const [classifications, setClassifications] = useState<{ [key: string]: string }>({});
  const [customLabels, setCustomLabels] = useState<{ [key: string]: string }>({});

  const cashFlowTypes = [
    { value: 'contribution', label: 'Contribution (Capital Call)', icon: <TrendingDown color="error" />, description: 'Money invested into the fund' },
    { value: 'distribution', label: 'Distribution (Payout)', icon: <TrendingUp color="success" />, description: 'Money returned from the fund' },
    { value: 'nav', label: 'Net Asset Value', icon: <AccountBalance color="primary" />, description: 'Fund valuation at specific dates' },
    { value: 'fee', label: 'Management Fee', icon: <SwapVert color="warning" />, description: 'Management or administrative fees' },
    { value: 'other_income', label: 'Other Income', icon: <TrendingUp color="info" />, description: 'Interest, dividends, or other income' },
    { value: 'expense', label: 'Expense', icon: <TrendingDown color="warning" />, description: 'Fund operating expenses' },
    { value: 'ignore', label: 'Ignore Column', icon: <HelpOutline color="disabled" />, description: 'Skip this column in analysis' }
  ];

  const handleClassificationChange = (columnName: string, type: string) => {
    setClassifications(prev => ({
      ...prev,
      [columnName]: type
    }));
  };

  const handleCustomLabelChange = (columnName: string, label: string) => {
    setCustomLabels(prev => ({
      ...prev,
      [columnName]: label
    }));
  };

  const handleSubmit = () => {
    const finalClassifications = { ...classifications };
    
    // Add custom labels where provided
    Object.keys(customLabels).forEach(columnName => {
      if (customLabels[columnName].trim()) {
        finalClassifications[columnName] = customLabels[columnName].trim();
      }
    });

    onClassify(finalClassifications);
  };

  const getPatternAnalysis = (patterns: string[]) => {
    const analysis = [];
    
    if (patterns.includes('negative_values')) {
      analysis.push('Contains negative values (likely outflows/contributions)');
    }
    if (patterns.includes('positive_values')) {
      analysis.push('Contains positive values (likely inflows/distributions)');
    }
    if (patterns.includes('percentage_like')) {
      analysis.push('Values appear to be percentages or ratios');
    }
    if (patterns.includes('large_amounts')) {
      analysis.push('Contains large monetary amounts');
    }
    if (patterns.includes('date_correlation')) {
      analysis.push('Values correlate with date patterns');
    }
    if (patterns.includes('quarterly_pattern')) {
      analysis.push('Shows quarterly reporting pattern');
    }
    
    return analysis;
  };

  const getSmartSuggestion = (column: UnclassifiedColumn) => {
    const { sampleValues, detectedPatterns, columnName } = column;
    
    // Analyze column name for hints
    const nameHints = columnName.toLowerCase();
    if (nameHints.includes('call') || nameHints.includes('contribution') || nameHints.includes('commit')) {
      return 'contribution';
    }
    if (nameHints.includes('distribution') || nameHints.includes('payout') || nameHints.includes('return')) {
      return 'distribution';
    }
    if (nameHints.includes('nav') || nameHints.includes('value') || nameHints.includes('valuation')) {
      return 'nav';
    }
    if (nameHints.includes('fee') || nameHints.includes('expense') || nameHints.includes('cost')) {
      return 'fee';
    }

    // Analyze patterns
    if (detectedPatterns.includes('negative_values') && !detectedPatterns.includes('positive_values')) {
      return 'contribution';
    }
    if (detectedPatterns.includes('positive_values') && !detectedPatterns.includes('negative_values')) {
      return 'distribution';
    }
    if (detectedPatterns.includes('percentage_like')) {
      return 'nav';
    }

    return null;
  };

  const allClassified = unclassifiedColumns.every(col => 
    classifications[col.columnName] || col.suggestedType
  );

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: isDarkMode ? '#0a0a0a' : 'background.paper',
          minHeight: '80vh'
        }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <Lightbulb color="primary" />
          <Box>
            <Typography variant="h5">
              Cash Flow Classification Required
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {fileName} - {unclassifiedColumns.length} columns need classification
            </Typography>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            Our AI detected some cash flow columns but couldn't determine their exact type. 
            Please help classify these columns so we can properly analyze your data.
          </Typography>
        </Alert>

        {unclassifiedColumns.map((column, index) => {
          const smartSuggestion = getSmartSuggestion(column);
          const patternAnalysis = getPatternAnalysis(column.detectedPatterns);
          
          return (
            <Card key={index} sx={{ mb: 3, backgroundColor: isDarkMode ? '#111' : 'background.default' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Column: "{column.columnName}"
                    </Typography>
                    <Chip
                      size="small"
                      label={`Confidence: ${(column.confidence * 100).toFixed(0)}%`}
                      color={column.confidence > 0.7 ? 'success' : column.confidence > 0.4 ? 'warning' : 'error'}
                    />
                  </Box>
                  
                  {smartSuggestion && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleClassificationChange(column.columnName, smartSuggestion)}
                      startIcon={<Lightbulb />}
                    >
                      Use AI Suggestion
                    </Button>
                  )}
                </Box>

                {/* Sample Data Preview */}
                <Accordion sx={{ mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="body2">Sample Data & Patterns</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box display="flex" gap={3}>
                      <Box flex={1}>
                        <Typography variant="subtitle2" gutterBottom>Sample Values:</Typography>
                        <Box display="flex" flexWrap="wrap" gap={1}>
                          {column.sampleValues.slice(0, 5).map((value, i) => (
                            <Chip key={i} label={value} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </Box>
                      
                      <Box flex={1}>
                        <Typography variant="subtitle2" gutterBottom>Detected Patterns:</Typography>
                        <List dense>
                          {patternAnalysis.map((analysis, i) => (
                            <ListItem key={i}>
                              <ListItemIcon>
                                <TrendingUp fontSize="small" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={analysis}
                                primaryTypographyProps={{ variant: 'body2' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    </Box>
                  </AccordionDetails>
                </Accordion>

                {/* Classification Selection */}
                <FormControl fullWidth variant="outlined">
                  <InputLabel>Classify this column as...</InputLabel>
                  <Select
                    value={classifications[column.columnName] || smartSuggestion || ''}
                    onChange={(e) => handleClassificationChange(column.columnName, e.target.value)}
                    label="Classify this column as..."
                  >
                    {cashFlowTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        <Box display="flex" alignItems="center" gap={2}>
                          {type.icon}
                          <Box>
                            <Typography variant="body2">{type.label}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {type.description}
                            </Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                    ))}
                    <MenuItem value="custom">
                      <Box display="flex" alignItems="center" gap={2}>
                        <HelpOutline color="primary" />
                        <Typography variant="body2">Custom Type</Typography>
                      </Box>
                    </MenuItem>
                  </Select>
                </FormControl>

                {/* Custom Label Input */}
                {classifications[column.columnName] === 'custom' && (
                  <TextField
                    fullWidth
                    label="Custom Cash Flow Type"
                    placeholder="e.g., Preferred Return, Catch-up Distribution"
                    value={customLabels[column.columnName] || ''}
                    onChange={(e) => handleCustomLabelChange(column.columnName, e.target.value)}
                    sx={{ mt: 2 }}
                    helperText="Describe what this cash flow represents"
                  />
                )}

                {/* AI Suggestion Display */}
                {smartSuggestion && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>AI Suggestion:</strong> Based on the column name and data patterns, 
                      this appears to be a <strong>{cashFlowTypes.find(t => t.value === smartSuggestion)?.label}</strong>
                    </Typography>
                  </Alert>
                )}
              </CardContent>
            </Card>
          );
        })}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose} color="inherit">
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={!allClassified}
        >
          Apply Classifications ({Object.keys(classifications).length}/{unclassifiedColumns.length})
        </Button>
      </DialogActions>
    </Dialog>
  );
}; 