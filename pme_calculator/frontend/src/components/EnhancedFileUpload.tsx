import React, { useState, useCallback, useEffect } from 'react';
import {
  Box, Typography, Button, Card, CardContent, Alert, 
  LinearProgress, Chip, Paper, Divider
} from '@mui/material';
import {
  Cloud, CheckCircle, AlertTriangle, FileText, 
  Folder, BarChart3, Upload, X
} from 'lucide-react';
import { analysisService } from '../services/analysisService';
import { fileStore } from '../services/fileStore';
import { useNavigate } from 'react-router-dom';

interface FileUploadState {
  file: File | null;
  status: 'idle' | 'uploading' | 'success' | 'error';
  error: string | null;
  id: string | null;
}

interface EnhancedFileUploadProps {
  type: 'fund' | 'index';
  title: string;
  description: string;
  icon: React.ReactNode;
  required?: boolean;
}

export const EnhancedFileUpload: React.FC<EnhancedFileUploadProps> = ({
  type,
  title,
  description,
  icon,
  required = false
}) => {
  const [uploadState, setUploadState] = useState<FileUploadState>({
    file: null,
    status: 'idle',
    error: null,
    id: null
  });
  const [dragActive, setDragActive] = useState(false);

  // Sync with file store on mount and when store changes
  useEffect(() => {
    const unsubscribe = fileStore.subscribe((storeState) => {
      const storeFile = type === 'fund' ? storeState.fundFile : storeState.indexFile;
      
      if (storeFile && !uploadState.id) {
        // File exists in store but not in local state - sync it
        setUploadState({
          file: null, // We don't have the original File object, that's fine
          status: 'success',
          error: null,
          id: storeFile.id
        });
        console.log(`Synced ${type} file from store:`, storeFile);
      } else if (!storeFile && uploadState.id) {
        // File removed from store - reset local state
        setUploadState({
          file: null,
          status: 'idle',
          error: null,
          id: null
        });
        console.log(`Reset ${type} file state - removed from store`);
      }
    });

    return unsubscribe;
  }, [type, uploadState.id]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  }, []);

  const handleFileSelection = (file: File) => {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadState({
        file: null,
        status: 'error',
        error: 'Please select a CSV file',
        id: null
      });
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setUploadState({
        file: null,
        status: 'error',
        error: 'File size must be less than 10MB',
        id: null
      });
      return;
    }

    setUploadState({
      file,
      status: 'idle',
      error: null,
      id: null
    });
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!uploadState.file) return;

    setUploadState(prev => ({ ...prev, status: 'uploading', error: null }));

    try {
      const response = await analysisService.uploadFile(uploadState.file, type);
      
      if (response.success && response.file_id) {
        setUploadState(prev => ({
          ...prev,
          status: 'success',
          id: response.file_id
        }));

        // Update file store
        const fileData = {
          id: response.file_id,
          name: uploadState.file!.name,
          type
        };

        if (type === 'fund') {
          fileStore.addFundFile(fileData);
        } else {
          fileStore.addIndexFile(fileData);
        }
      } else {
        throw new Error(response.message || 'Upload failed');
      }
    } catch (error: any) {
      setUploadState(prev => ({
        ...prev,
        status: 'error',
        error: error.message || 'Upload failed'
      }));
    }
  };

  const handleRemove = () => {
    setUploadState({
      file: null,
      status: 'idle',
      error: null,
      id: null
    });
    
    // Also remove from file store
    if (type === 'fund') {
      fileStore.clearFundFile();
    } else {
      fileStore.clearIndexFile();
    }
  };

  const getStatusColor = () => {
    switch (uploadState.status) {
      case 'success': return 'success.main';
      case 'error': return 'error.main';
      case 'uploading': return 'primary.main';
      default: return 'text.secondary';
    }
  };

  const getStatusIcon = () => {
    switch (uploadState.status) {
      case 'success': return <CheckCircle size={20} color="#22c55e" />;
      case 'error': return <AlertTriangle size={20} color="#ef4444" />;
      case 'uploading': return <LinearProgress />;
      default: return null;
    }
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: dragActive ? '2px dashed #3b82f6' : '1px solid #e5e7eb',
        backgroundColor: dragActive ? '#f8fafc' : 'background.paper',
        transition: 'all 0.3s ease'
      }}
    >
      <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          {icon}
          <Box>
            <Typography variant="h6" fontWeight="bold">
              {title}
              {required && <Chip label="Required" size="small" sx={{ ml: 1 }} />}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Upload Area */}
        <Box
          flex={1}
          display="flex"
          flexDirection="column"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {!uploadState.file && uploadState.status !== 'success' ? (
            <Paper
              sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                border: '2px dashed #d1d5db',
                borderRadius: 2,
                p: 3,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: '#3b82f6',
                  backgroundColor: '#f8fafc'
                }
              }}
              component="label"
            >
              <Cloud size={48} color="#6b7280" />
              <Typography variant="h6" color="text.secondary" mt={2} mb={1}>
                Drop your CSV file here
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                or click to browse
              </Typography>
              <Button variant="outlined" component="span">
                Browse Files
              </Button>
              <input
                type="file"
                hidden
                accept=".csv"
                onChange={handleFileInputChange}
              />
              <Typography variant="caption" color="text.secondary" mt={2}>
                Supports CSV files up to 10MB
              </Typography>
            </Paper>
          ) : (
            <Box flex={1}>
              {/* File Info */}
              <Paper sx={{ p: 2, mb: 2, backgroundColor: 'grey.50' }}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center" gap={2}>
                    <FileText size={24} />
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {uploadState.file ? uploadState.file.name : (() => {
                          const storeState = fileStore.getState();
                          const storeFile = type === 'fund' ? storeState.fundFile : storeState.indexFile;
                          return storeFile ? storeFile.name : 'Unknown file';
                        })()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {uploadState.file ? `${(uploadState.file.size / 1024).toFixed(1)} KB` : 'Restored from backend'}
                      </Typography>
                    </Box>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getStatusIcon()}
                    <Button
                      size="small"
                      onClick={handleRemove}
                      disabled={uploadState.status === 'uploading'}
                    >
                      <X size={16} />
                    </Button>
                  </Box>
                </Box>
              </Paper>

              {/* Upload Progress */}
              {uploadState.status === 'uploading' && (
                <Box mb={2}>
                  <LinearProgress />
                  <Typography variant="caption" color="text.secondary" mt={1}>
                    Uploading and validating file...
                  </Typography>
                </Box>
              )}

              {/* Error Message */}
              {uploadState.error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {uploadState.error}
                </Alert>
              )}

              {/* Success Message */}
              {uploadState.status === 'success' && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  File uploaded successfully! File ID: {uploadState.id}
                </Alert>
              )}
            </Box>
          )}
        </Box>

        {/* Action Buttons */}
        <Box display="flex" gap={2} mt={2}>
          {uploadState.file && uploadState.status !== 'success' && (
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={uploadState.status === 'uploading'}
              startIcon={<Upload />}
              fullWidth
            >
              {uploadState.status === 'uploading' ? 'Uploading...' : 'Upload File'}
            </Button>
          )}
          {uploadState.status === 'success' && (
            <Button
              variant="outlined"
              onClick={handleRemove}
              startIcon={<Cloud />}
              fullWidth
            >
              Upload Different File
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}; 