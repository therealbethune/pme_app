import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Container, Button, Alert, Card, CardContent,
  Tabs, Tab, Grid, Chip, LinearProgress, Divider
} from '@mui/material';
import { 
  TrendingUp, AttachMoney, PieChart, BarChart, 
  Download, EmojiEvents, Calculate, Timeline
} from '@mui/icons-material';
import { useColorMode } from '../contexts/ColorModeContext';
import { AnalysisDashboard } from '../components/AnalysisDashboard';
import { PMECharts } from '../components/PMECharts';
import { InteractiveFilters } from '../components/InteractiveFilters';
import { ChartsDashboard } from '../components/ChartsDashboard';

interface PMEMetrics {
  kaplan_schoar_pme?: number;
  pme_plus_lambda?: number;
  direct_alpha?: number;
  long_nickels_pme?: number;
  fund_irr?: number;
  benchmark_irr?: number;
  alpha?: number;
}

interface AnalysisData {
  success: boolean;
  metrics: {
    'Fund IRR': number;
    'TVPI': number;
    'DPI': number;
    'RVPI': number;
    'MOIC': number;
    'Total Contributions': number;
    'Total Distributions': number;
    'Final NAV': number;
  } & { pme_metrics?: PMEMetrics };
  has_benchmark: boolean;
  analysis_date: string;
  summary?: any;
}

const Analysis: React.FC = () => {
  const { isDarkMode } = useColorMode();
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [filterCriteria, setFilterCriteria] = useState<any>(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get uploaded files
      const filesResponse = await fetch('/api/upload/files');
      const filesData = await filesResponse.json();
      
      // Convert files object to array for easier processing
      const filesArray = Object.entries(filesData.files || {}).map(([id, fileInfo]: [string, any]) => ({
        id,
        ...fileInfo
      }));
      
      const fundFile = filesArray.find((f: any) => f.type === 'fund');
      const indexFile = filesArray.find((f: any) => f.type === 'index');
      
      if (!fundFile) {
        throw new Error('No fund file uploaded. Please upload a fund cashflow file first.');
      }
      
      // Run analysis
      let url = `/api/analysis/run?fund_file_id=${fundFile.id}`;
      if (indexFile) {
        url += `&index_file_id=${indexFile.id}`;
      }
      
      const response = await fetch(url, { method: 'POST' });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }
      
      const data = await response.json();
      setAnalysisData(data);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const exportAnalysis = () => {
    if (!analysisData) return;
    
    const dataStr = JSON.stringify(analysisData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pme-analysis-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  // PME Performance Assessment
  const getPMEPerformance = (ks_pme: number) => {
    if (ks_pme >= 1.3) return { label: 'Exceptional', color: '#22c55e', bg: '#dcfce7' };
    if (ks_pme >= 1.15) return { label: 'Strong', color: '#3b82f6', bg: '#dbeafe' };
    if (ks_pme >= 1.0) return { label: 'Good', color: '#f59e0b', bg: '#fef3c7' };
    if (ks_pme >= 0.85) return { label: 'Below Market', color: '#f97316', bg: '#fed7aa' };
    return { label: 'Poor', color: '#ef4444', bg: '#fecaca' };
  };

  const formatPercent = (value: number, decimals = 1) => 
    `${(value * 100).toFixed(decimals)}%`;

  const formatDecimal = (value: number, decimals = 3) => 
    value.toFixed(decimals);

  const pmeMetrics = analysisData?.metrics?.pme_metrics;
  const ksPerformance = pmeMetrics?.kaplan_schoar_pme ? 
    getPMEPerformance(pmeMetrics.kaplan_schoar_pme) : null;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: isDarkMode ? '#000000' : '#f8fafc',
        pt: 2
      }}
    >
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom display="flex" alignItems="center" gap={1}>
          <EmojiEvents sx={{ color: '#3b82f6' }} />
          PME Analysis Dashboard
        </Typography>
        
        <Typography variant="body1" color="text.secondary" mb={3}>
          Comprehensive performance measurement and benchmarking analysis
        </Typography>

        {!analysisData && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Ready to analyze your fund performance?
              </Typography>
              <Button 
                variant="contained" 
                size="large"
                onClick={runAnalysis}
                disabled={loading}
                startIcon={loading ? undefined : <Calculate />}
              >
                {loading ? 'Running Analysis...' : 'Run PME Analysis'}
              </Button>
            </CardContent>
          </Card>
        )}

        {loading && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" mb={2}>
                🔍 Analyzing Fund Performance...
              </Typography>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary" mb={2}>
                Computing IRR, TVPI, PME metrics, and generating insights...
              </Typography>
              <Typography variant="caption" color="text.secondary">
                This may take a few moments for large datasets.
              </Typography>
            </CardContent>
          </Card>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6">Analysis Error</Typography>
            {error}
          </Alert>
        )}

        {analysisData && (
          <>
            {/* Header with Key Performance Indicator */}
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" mb={1}>
                      Analysis Complete
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Fund analyzed on {new Date(analysisData.analysis_date).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Box display="flex" gap={2} alignItems="center">
                    {ksPerformance && (
                      <Chip 
                        label={`PME: ${ksPerformance.label}`}
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
                      onClick={exportAnalysis}
                    >
                      Export Report
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Navigation Tabs */}
            <Card sx={{ mb: 3 }}>
              <Tabs 
                value={activeTab} 
                onChange={(_, newValue) => setActiveTab(newValue)}
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab label="Complete Dashboard" icon={<BarChart />} iconPosition="start" />
                <Tab label="PME Metrics" icon={<Calculate />} iconPosition="start" />
                <Tab label="Performance Summary" icon={<TrendingUp />} iconPosition="start" />
                <Tab label="Charts & Visualizations" icon={<Timeline />} iconPosition="start" />
                <Tab label="Interactive Charts" icon={<PieChart />} iconPosition="start" />
              </Tabs>
            </Card>

            {/* Tab Content */}
            {activeTab === 0 && (
              <AnalysisDashboard 
                data={analysisData} 
                onExport={exportAnalysis}
              />
            )}

            {activeTab === 1 && (
              <Grid container spacing={3}>
                {analysisData.has_benchmark ? (
                  <>
                    {/* PME Metrics Display */}
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
                              {formatDecimal(pmeMetrics?.kaplan_schoar_pme || 0)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {(pmeMetrics?.kaplan_schoar_pme || 0) > 1 ? 'Outperformed' : 'Underperformed'} public markets
                            </Typography>
                          </Box>

                          {pmeMetrics?.pme_plus_lambda && (
                            <Box mb={3}>
                              <Typography variant="subtitle2" color="text.secondary" mb={1}>
                                PME+ Lambda (Burgiss Method)
                              </Typography>
                              <Typography variant="h5" fontWeight="bold">
                                {formatDecimal(pmeMetrics.pme_plus_lambda)}
                              </Typography>
                            </Box>
                          )}

                          {pmeMetrics?.direct_alpha !== undefined && (
                            <Box mb={3}>
                              <Typography variant="subtitle2" color="text.secondary" mb={1}>
                                Direct Alpha
                              </Typography>
                              <Typography variant="h5" fontWeight="bold" 
                                color={pmeMetrics.direct_alpha > 0 ? '#22c55e' : '#ef4444'}
                              >
                                {formatPercent(pmeMetrics.direct_alpha, 2)}
                              </Typography>
                            </Box>
                          )}
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
                              {formatPercent(pmeMetrics?.fund_irr || analysisData.metrics['Fund IRR'])}
                            </Typography>
                          </Box>

                          {pmeMetrics?.benchmark_irr && (
                            <Box mb={3}>
                              <Typography variant="subtitle2" color="text.secondary" mb={1}>
                                Benchmark IRR
                              </Typography>
                              <Typography variant="h5" fontWeight="bold">
                                {formatPercent(pmeMetrics.benchmark_irr)}
                              </Typography>
                            </Box>
                          )}

                          {pmeMetrics?.alpha !== undefined && (
                            <Box mb={3}>
                              <Typography variant="subtitle2" color="text.secondary" mb={1}>
                                Alpha (Excess Return)
                              </Typography>
                              <Typography variant="h4" fontWeight="bold" 
                                color={pmeMetrics.alpha > 0 ? '#22c55e' : '#ef4444'}
                              >
                                {formatPercent(pmeMetrics.alpha, 2)}
                              </Typography>
                              <LinearProgress 
                                variant="determinate" 
                                value={Math.min(Math.abs(pmeMetrics.alpha) * 1000, 100)} 
                                color={pmeMetrics.alpha > 0 ? 'success' : 'error'}
                                sx={{ mt: 1, height: 8, borderRadius: 4 }}
                              />
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  </>
                ) : (
                  <Grid item xs={12}>
                    <Alert severity="warning" sx={{ mb: 3 }}>
                      <Typography variant="h6">PME calculations require benchmark data</Typography>
                      <Typography>
                        Upload index data for complete PME analysis including Kaplan-Schoar PME, 
                        PME+ Lambda, and Direct Alpha calculations.
                      </Typography>
                    </Alert>
                  </Grid>
                )}
              </Grid>
            )}

            {activeTab === 2 && (
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Fund IRR
                        </Typography>
                        <TrendingUp sx={{ color: '#22c55e' }} />
                      </Box>
                      <Typography variant="h4" fontWeight="bold">
                        {formatPercent(analysisData.metrics['Fund IRR'])}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          TVPI
                        </Typography>
                        <AttachMoney sx={{ color: '#3b82f6' }} />
                      </Box>
                      <Typography variant="h4" fontWeight="bold">
                        {analysisData.metrics['TVPI'].toFixed(2)}x
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          DPI
                        </Typography>
                        <PieChart sx={{ color: '#f59e0b' }} />
                      </Box>
                      <Typography variant="h4" fontWeight="bold">
                        {analysisData.metrics['DPI'].toFixed(2)}x
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          RVPI
                        </Typography>
                        <BarChart sx={{ color: '#6b7280' }} />
                      </Box>
                      <Typography variant="h4" fontWeight="bold">
                        {analysisData.metrics['RVPI'].toFixed(2)}x
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {activeTab === 3 && (
              <>
                {/* Filters */}
                <InteractiveFilters
                  onFilterChange={setFilterCriteria}
                  availableQuarters={[]}
                  currentMetrics={{
                    irr: { min: -0.2, max: 0.4, current: analysisData.metrics['Fund IRR'] },
                    tvpi: { min: 0.5, max: 3.0, current: analysisData.metrics['TVPI'] },
                    dpi: { min: 0, max: 2.0, current: analysisData.metrics['DPI'] }
                  }}
                  hasBenchmark={analysisData.has_benchmark}
                />

                {/* Charts */}
                <PMECharts
                  data={{
                    performance_timeline: [],
                    j_curve_data: [],
                    cash_flow_timeline: [],
                    twr_data: [],
                    metrics: analysisData.metrics,
                    has_benchmark: analysisData.has_benchmark
                  }}
                />
              </>
            )}

            {activeTab === 4 && (
              <ChartsDashboard analysisComplete={true} />
            )}

            {!analysisData.has_benchmark && (
              <Alert severity="warning" sx={{ mt: 3 }}>
                <Typography variant="h6">💡 Enhanced Analysis Available</Typography>
                Upload benchmark/index data to unlock advanced PME calculations including:
                <ul>
                  <li>Kaplan-Schoar PME</li>
                  <li>PME+ (Burgiss Method)</li>
                  <li>Direct Alpha measurement</li>
                  <li>Long-Nickels PME</li>
                  <li>Statistical confidence intervals</li>
                </ul>
              </Alert>
            )}
          </>
        )}
      </Container>
    </Box>
  );
};

export default Analysis; 