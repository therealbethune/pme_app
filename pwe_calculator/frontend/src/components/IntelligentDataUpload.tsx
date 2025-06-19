import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  CloudUpload, 
  BarChart3, 
  CheckCircle, 
  AlertTriangle, 
  Trash2, 
  FolderOpen,
  Loader2,
  Play
} from 'lucide-react';
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

  const renderStatusIcon = (status: UploadStatus['status']) => {
    switch (status) {
      case 'pending': return <CloudUpload className="w-5 h-5 text-gray-400" />;
      case 'uploading': return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default: return null;
    }
  };

  const fundUpload = uploads.find(u => u.type === 'fund');
  const indexUpload = uploads.find(u => u.type === 'index');
  const canAnalyze = !!fileStore.getState().fundFile;
  const hasPendingUploads = uploads.some(u => u.status === 'pending');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-white rounded-xl border border-gray-200 shadow-sm p-6"
    >
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Fund File Upload */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 mb-3">
            <FolderOpen className="w-5 h-5 text-brand" />
            <h3 className="text-lg font-semibold text-gray-900">1. Upload Fund File</h3>
          </div>
          
          <label className="block">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-brand transition-colors cursor-pointer">
              <CloudUpload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <span className="text-sm text-gray-600">Click to select fund data file</span>
            </div>
            <input
              type="file"
              className="hidden"
              onChange={(e) => handleFileChange(e, 'fund')}
              accept=".csv,.xlsx,.xls"
            />
          </label>

          {fundUpload && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              {renderStatusIcon(fundUpload.status)}
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{fundUpload.file.name}</p>
                <p className="text-xs text-gray-500">
                  {fundUpload.error || fundUpload.status}
                </p>
              </div>
            </motion.div>
          )}
        </div>

        {/* Index File Upload */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 mb-3">
            <BarChart3 className="w-5 h-5 text-brand" />
            <h3 className="text-lg font-semibold text-gray-900">2. Upload Index File</h3>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">Optional</span>
          </div>
          
          <label className="block">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-brand transition-colors cursor-pointer">
              <BarChart3 className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <span className="text-sm text-gray-600">Click to select benchmark index</span>
            </div>
            <input
              type="file"
              className="hidden"
              onChange={(e) => handleFileChange(e, 'index')}
              accept=".csv,.xlsx,.xls"
            />
          </label>

          {indexUpload && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              {renderStatusIcon(indexUpload.status)}
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{indexUpload.file.name}</p>
                <p className="text-xs text-gray-500">
                  {indexUpload.error || indexUpload.status}
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <button
          onClick={clearUploads}
          className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-red-600 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          <span>Clear All</span>
        </button>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleUpload}
            disabled={!hasPendingUploads}
            className="flex items-center space-x-2 px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CloudUpload className="w-4 h-4" />
            <span>Upload Files</span>
          </button>

          <button
            onClick={handleRunAnalysis}
            disabled={!canAnalyze || isAnalyzing || hasPendingUploads}
            className="flex items-center space-x-2 px-6 py-3 bg-brand text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isAnalyzing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{isAnalyzing ? 'Running Analysis...' : 'Run Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Error Message */}
      {analysisError && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <p className="text-sm text-red-700">{analysisError}</p>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}; 