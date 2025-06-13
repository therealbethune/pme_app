import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Container, Card, CardContent, Button, 
  Alert, Divider, Stepper, Step, StepLabel, Paper, Chip
} from '@mui/material';
import { 
  Folder, BarChart3, PlayCircle, CheckCircle, TrendingUp 
} from 'lucide-react';
import { EnhancedFileUpload } from './EnhancedFileUpload';
import { fileStore } from '../services/fileStore';
import { analysisService } from '../services/analysisService';
import { useNavigate } from 'react-router-dom';

export const EnhancedDataUpload: React.FC = () => {
  const [fileStoreState, setFileStoreState] = useState(fileStore.getState());
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [isLoadingFiles, setIsLoadingFiles] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const unsubscribe = fileStore.subscribe((newState) => {
      console.log('EnhancedDataUpload - File store updated:', newState);
      setFileStoreState(newState);
    });
    
    // Force immediate state sync
    const initialState = fileStore.getState();
    console.log('EnhancedDataUpload - Initial state:', initialState);
    setFileStoreState(initialState);
    
    // Restore files from backend when component mounts
    const restoreFiles = async () => {
      console.log('EnhancedDataUpload - Starting file restoration...');
      try {
        await fileStore.restoreFilesFromBackend();
        const currentState = fileStore.getState();
        console.log('EnhancedDataUpload - Files restored, current state:', currentState);
        setFileStoreState(currentState);
      } catch (error) {
        console.error('EnhancedDataUpload - Error restoring files:', error);
      } finally {
        setIsLoadingFiles(false);
      }
    };
    
    restoreFiles();
    
    return unsubscribe;
  }, []);

  const handleRunAnalysis = async () => {
    if (!fileStoreState.fundFile?.id) {
      setAnalysisError("Please upload a fund file first.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      const results = await analysisService.runAnalysis(
        fileStoreState.fundFile.id, 
        fileStoreState.indexFile?.id
      );
      
      if (results.success) {
        fileStore.setAnalysisResults(results);
        navigate('/analysis');
      } else {
        throw new Error(results.detail || 'Analysis failed');
      }
    } catch (err: any) {
      setAnalysisError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getActiveStep = () => {
    if (!fileStoreState.fundFile) return 0;
    if (!fileStoreState.indexFile) return 1;
    return 2;
  };

  const canRunAnalysis = !!fileStoreState.fundFile;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Upload Your Data
        </Typography>
        <Typography variant="body1" color="text.secondary" mb={3}>
          Upload your fund performance data and optional benchmark index data to begin PME analysis.
        </Typography>

        {/* Progress Stepper */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Stepper activeStep={getActiveStep()} alternativeLabel>
              <Step completed={!!fileStoreState.fundFile}>
                <StepLabel>Upload Fund Data</StepLabel>
              </Step>
              <Step completed={!!fileStoreState.indexFile}>
                <StepLabel>Upload Index Data (Optional)</StepLabel>
              </Step>
              <Step completed={false}>
                <StepLabel>Run Analysis</StepLabel>
              </Step>
            </Stepper>
          </CardContent>
        </Card>
      </Box>

      {/* Upload Section */}
      <Box display="grid" gridTemplateColumns={{ xs: '1fr', md: 'repeat(2, 1fr)' }} gap={4} mb={4}>
        <EnhancedFileUpload
          type="fund"
          title="Fund Performance Data"
          description="Upload CSV with Date, Cash Flow, and NAV columns"
          icon={<Folder size={24} color="#3b82f6" />}
          required
        />
        
        <EnhancedFileUpload
          type="index"
          title="Benchmark Index Data"
          description="Upload CSV with Date and Price columns"
          icon={<BarChart3 size={24} color="#10b981" />}
        />
      </Box>

      {/* Analysis Section */}
      <Card>
        <CardContent sx={{ p: 4 }}>
          <Box display="flex" alignItems="center" gap={2} mb={3}>
            <TrendingUp size={28} color="#6366f1" />
            <Typography variant="h5" fontWeight="bold">
              Ready to Analyze
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* File Status */}
          <Box mb={3}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6" gutterBottom>
                Uploaded Files
              </Typography>
              <Button 
                size="small" 
                onClick={async () => {
                  setIsLoadingFiles(true);
                  console.log('Manual refresh triggered');
                  try {
                    await fileStore.restoreFilesFromBackend();
                    const currentState = fileStore.getState();
                    console.log('Manual refresh - current state:', currentState);
                    setFileStoreState(currentState);
                  } catch (error) {
                    console.error('Manual refresh error:', error);
                  } finally {
                    setIsLoadingFiles(false);
                  }
                }}
                variant="outlined"
              >
                Refresh
              </Button>
            </Box>
            {isLoadingFiles ? (
              <Typography variant="body2" color="text.secondary">
                Loading uploaded files...
              </Typography>
            ) : (
              <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
                {fileStoreState.fundFile && (
                  <Chip
                    icon={<CheckCircle size={16} />}
                    label={`Fund: ${fileStoreState.fundFile.name}`}
                    color="success"
                    variant="outlined"
                  />
                )}
                {fileStoreState.indexFile && (
                  <Chip
                    icon={<CheckCircle size={16} />}
                    label={`Index: ${fileStoreState.indexFile.name}`}
                    color="info"
                    variant="outlined"
                  />
                )}
                {!fileStoreState.fundFile && !isLoadingFiles && (
                  <Chip
                    label="No fund file uploaded"
                    color="error"
                    variant="outlined"
                  />
                )}
              </Box>
            )}
          </Box>

          {/* Analysis Info */}
          <Paper sx={{ p: 3, mb: 3, backgroundColor: 'grey.50' }}>
            <Typography variant="subtitle1" fontWeight="bold" mb={2}>
              What will be calculated:
            </Typography>
            <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)' }} gap={2}>
              <Typography variant="body2">• Internal Rate of Return (IRR)</Typography>
              <Typography variant="body2">• Total Value to Paid-In (TVPI)</Typography>
              <Typography variant="body2">• Distributions to Paid-In (DPI)</Typography>
              <Typography variant="body2">• Residual Value to Paid-In (RVPI)</Typography>
              <Typography variant="body2">• Multiple of Invested Capital (MOIC)</Typography>
              {fileStoreState.indexFile && (
                <Typography variant="body2">• PME vs Benchmark Comparison</Typography>
              )}
            </Box>
          </Paper>

          {/* Success/Error Display */}
          {fileStoreState.fundFile && fileStoreState.indexFile && (
            <Alert severity="success" sx={{ mb: 3 }}>
              All files uploaded successfully! Ready for comprehensive PME analysis with benchmark comparison.
            </Alert>
          )}
          {fileStoreState.fundFile && !fileStoreState.indexFile && (
            <Alert severity="info" sx={{ mb: 3 }}>
              Fund data uploaded. Add benchmark index data for complete PME analysis, or run basic analysis without benchmark.
            </Alert>
          )}
          {analysisError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {analysisError}
            </Alert>
          )}

          {/* Analysis Button */}
          <Box display="flex" justifyContent="center">
            <Button
              variant="contained"
              size="large"
              onClick={handleRunAnalysis}
              disabled={!canRunAnalysis || isAnalyzing}
              startIcon={isAnalyzing ? undefined : <PlayCircle />}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                minWidth: 200
              }}
            >
              {isAnalyzing ? 'Analyzing...' : 'Run PME Analysis'}
            </Button>
          </Box>

          {!canRunAnalysis && (
            <Typography 
              variant="body2" 
              color="text.secondary" 
              textAlign="center" 
              mt={2}
            >
              Please upload fund data to enable analysis
            </Typography>
          )}
        </CardContent>
      </Card>
    </Container>
  );
}; 