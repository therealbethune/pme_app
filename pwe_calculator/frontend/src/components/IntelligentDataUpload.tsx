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
  Play,
  FileText,
  Database
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
      case 'uploading': return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
      case 'success': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error': return <AlertTriangle className="w-5 h-5 text-red-400" />;
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
      className="bg-gray-950 rounded-xl border border-gray-800 shadow-lg p-6"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Data Upload & Analysis</h2>
        <p className="text-gray-400">Upload your fund and benchmark data to begin PME analysis</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Fund File Upload */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 mb-3">
            <Database className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-white">1. Upload Fund Data</h3>
            <span className="status-error">Required</span>
          </div>
          
          <label className="block">
            <div className="border-2 border-dashed border-gray-700 rounded-lg p-6 text-center hover:border-primary hover:bg-gray-900/50 transition-all cursor-pointer">
              <CloudUpload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <span className="text-sm text-gray-300 block mb-1">Click to select fund data file</span>
              <span className="text-xs text-gray-500">Supports CSV, XLSX, XLS</span>
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
              className="flex items-center space-x-3 p-4 bg-gray-900 rounded-lg border border-gray-800"
            >
              {renderStatusIcon(fundUpload.status)}
              <div className="flex-1">
                <p className="text-sm font-medium text-white">{fundUpload.file.name}</p>
                <p className="text-xs text-gray-400">
                  {fundUpload.error || fundUpload.status}
                </p>
              </div>
              {fundUpload.status === 'success' && (
                <div className="status-success">
                  <CheckCircle className="w-4 h-4" />
                </div>
              )}
            </motion.div>
          )}
        </div>

        {/* Index File Upload */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 mb-3">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-white">2. Upload Benchmark</h3>
            <span className="status-info">Optional</span>
          </div>
          
          <label className="block">
            <div className="border-2 border-dashed border-gray-700 rounded-lg p-6 text-center hover:border-primary hover:bg-gray-900/50 transition-all cursor-pointer">
              <BarChart3 className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <span className="text-sm text-gray-300 block mb-1">Click to select benchmark index</span>
              <span className="text-xs text-gray-500">Market index for comparison</span>
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
              className="flex items-center space-x-3 p-4 bg-gray-900 rounded-lg border border-gray-800"
            >
              {renderStatusIcon(indexUpload.status)}
              <div className="flex-1">
                <p className="text-sm font-medium text-white">{indexUpload.file.name}</p>
                <p className="text-xs text-gray-400">
                  {indexUpload.error || indexUpload.status}
                </p>
              </div>
              {indexUpload.status === 'success' && (
                <div className="status-success">
                  <CheckCircle className="w-4 h-4" />
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-gray-800">
        <div className="flex gap-3 flex-1">
          {hasPendingUploads && (
            <button
              onClick={handleUpload}
              className="btn-primary flex-1"
            >
              <CloudUpload className="w-4 h-4 mr-2" />
              Upload Files
            </button>
          )}
          
          {uploads.length > 0 && (
            <button
              onClick={clearUploads}
              className="btn-ghost"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear
            </button>
          )}
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={!canAnalyze || isAnalyzing}
          className={`btn-primary ${(!canAnalyze || isAnalyzing) ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Running Analysis...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Run PME Analysis
            </>
          )}
        </button>
      </div>

      {/* Analysis Error */}
      {analysisError && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 bg-red-900/20 border border-red-800 rounded-lg p-4 flex items-start"
        >
          <AlertTriangle className="w-5 h-5 text-red-400 mr-3 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-red-400 font-medium mb-1">Analysis Error</h4>
            <p className="text-red-300 text-sm">{analysisError}</p>
          </div>
        </motion.div>
      )}

      {/* Upload Instructions */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-6 bg-gray-900/50 rounded-lg p-4"
      >
        <h4 className="text-white font-medium mb-2 flex items-center">
          <FileText className="w-4 h-4 mr-2 text-primary" />
          File Format Requirements
        </h4>
        <ul className="text-sm text-gray-400 space-y-1">
          <li>• Fund data should include dates, cash flows, and valuations</li>
          <li>• Benchmark data should include dates and index values</li>
          <li>• Supported formats: CSV, Excel (XLSX, XLS)</li>
          <li>• Ensure dates are in a consistent format</li>
        </ul>
      </motion.div>
    </motion.div>
  );
}; 