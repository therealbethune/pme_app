import React, { useState } from 'react';
import {
  Box, Typography, Button, Card, CardContent, Alert, ListItem, ListItemIcon, ListItemText, Divider, CircularProgress, Grid
} from '@mui/material';
import { CloudUpload, Analytics, CheckCircle, Warning, DeleteOutline, Folder, BarChart } from '@mui/icons-material';
import { analysisService } from '../services/analysisService';
import { fileStore } from '../services/fileStore';
import { useNavigate } from 'react-router-dom';

interface UploadStatus {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  id: string | null;
  error?: string;
  type: 'fund' | 'index';
}

export const IntelligentDataUpload: React.FC = () => {
  const [uploads, setUploads] = useState<UploadStatus[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>, type: 'fund' | 'index') => {
    const selectedFiles = Array.from(event.target.files || []);
    if (selectedFiles.length > 0) {
      const newUpload: UploadStatus = {
        file: selectedFiles[0],
        status: 'pending',
        id: null,
        type,
      };
      setUploads(prev => [...prev.filter(u => u.type !== type), newUpload]);
    }
  };

  const clearUploads = () => {
    setUploads([]);
    fileStore.clearFiles();
    setAnalysisError(null);
  };

  const handleUpload = async () => {
    const pendingUploads = uploads.filter(u => u.status === 'pending');
    if (pendingUploads.length === 0) return;

    setUploads(prev => prev.map(u => (u.status === 'pending' ? { ...u, status: 'uploading' } : u)));

    const uploadPromises = pendingUploads.map(async (upload) => {
      try {
        const response = await analysisService.uploadFile(upload.file, upload.type);
        if (response.success && response.file_id) {
          const newStatus: UploadStatus = { ...upload, status: 'success', id: response.file_id };
          if (newStatus.type === 'fund') fileStore.addFundFile({ id: response.file_id, name: newStatus.file.name, type: 'fund' });
          if (newStatus.type === 'index') fileStore.addIndexFile({ id: response.file_id, name: newStatus.file.name, type: 'index' });
          return newStatus;
        } else {
          throw new Error(response.message || 'Upload failed');
        }
      } catch (err: any) {
        return { ...upload, status: 'error' as 'error', error: err.message };
      }
    });

    const results = await Promise.all(uploadPromises);
    setUploads(prev => prev.map(u => results.find(res => res.file.name === u.file.name && res.type === u.type) || u));
  };

  const handleRunAnalysis = async () => {
    const fundState = fileStore.getState().fundFile;
    if (!fundState?.id) {
      setAnalysisError("A successfully uploaded fund file is required.");
      return;
    }
    const indexState = fileStore.getState().indexFile;
    
    setIsAnalyzing(true);
    setAnalysisError(null);
    try {
      const results = await analysisService.runAnalysis(fundState.id, indexState?.id);
      if (results.success) {
        fileStore.setAnalysisResults(results);
        navigate('/analysis');
      } else {
        throw new Error(results.detail || 'Analysis failed on the backend.');
      }
    } catch (err: any) {
      setAnalysisError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const fundUpload = uploads.find(u => u.type === 'fund');
  const indexUpload = uploads.find(u => u.type === 'index');
  const canAnalyze = !!fileStore.getState().fundFile;
  const hasPendingUploads = uploads.some(u => u.status === 'pending');

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card><CardContent>
            <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <Folder sx={{ mr: 1 }}/> 1. Upload Fund File
            </Typography>
            <Button variant="contained" component="label">Select File<input type="file" hidden onChange={e => handleFileChange(e, 'fund')} /></Button>
            {fundUpload && <ListItem><ListItemIcon>{renderStatusIcon(fundUpload.status)}</ListItemIcon><ListItemText primary={fundUpload.file.name} secondary={fundUpload.error || fundUpload.status} /></ListItem>}
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card><CardContent>
            <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <BarChart sx={{ mr: 1 }}/> 2. Upload Index File (Optional)
            </Typography>
            <Button variant="contained" component="label">Select File<input type="file" hidden onChange={e => handleFileChange(e, 'index')} /></Button>
            {indexUpload && <ListItem><ListItemIcon>{renderStatusIcon(indexUpload.status)}</ListItemIcon><ListItemText primary={indexUpload.file.name} secondary={indexUpload.error || indexUpload.status} /></ListItem>}
          </CardContent></Card>
        </Grid>
      </Grid>
      <Divider sx={{ my: 3 }} />
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Button startIcon={<DeleteOutline />} onClick={clearUploads} color="warning">Clear</Button>
        <Button startIcon={<CloudUpload />} onClick={handleUpload} disabled={!hasPendingUploads} variant="outlined">Upload</Button>
        <Button variant="contained" size="large" onClick={handleRunAnalysis} disabled={!canAnalyze || isAnalyzing || hasPendingUploads} startIcon={isAnalyzing ? <CircularProgress size={24} /> : <Analytics />}>Run Analysis</Button>
      </Box>
      {analysisError && <Alert severity="error" sx={{ mt: 2 }}>{analysisError}</Alert>}
    </Box>
  );
};

const renderStatusIcon = (status: UploadStatus['status']) => {
    switch (status) {
        case 'pending': return <CloudUpload color="action" />;
        case 'uploading': return <CircularProgress size={24} />;
        case 'success': return <CheckCircle color="success" />;
        case 'error': return <Warning color="error" />;
    }
}; 