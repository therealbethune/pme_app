# PME Calculator Migration Files

## Backend Files

### backend/api_bridge.py
```python
"""API Bridge for exposing Python functions to the React frontend via pywebview."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Add the pme_app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# TODO: Import your existing PME calculation modules here
# from pme_app.pme_calcs import compute_pme_metrics
# from pme_app.utils import load_fund_file, load_index_file
# from pme_app.gui.main_window import PMEApp  # for accessing existing logic

class ApiBridge:
    """Bridge class that exposes Python methods to the frontend via pywebview."""
    
    def __init__(self):
        self.fund_data = None
        self.index_data = None
        self.last_analysis_results = None
    
    def fund_metrics(self, file_path: str) -> Dict[str, Any]:
        """
        Calculate fund metrics from uploaded file.
        
        TODO: Replace this with your existing PME calculation logic
        """
        try:
            # TODO: Use your existing load_fund_file function
            # self.fund_data = load_fund_file(file_path)
            
            # Placeholder implementation - replace with actual logic
            df = pd.read_csv(file_path)
            
            # TODO: Use your existing compute_pme_metrics function
            # metrics = compute_pme_metrics(self.fund_data, self.index_data)
            
            # Placeholder metrics - replace with actual calculations
            metrics = {
                'irr': 0.15,  # 15%
                'tvpi': 2.5,
                'dpi': 1.8,
                'rvpi': 0.7,
                'pme': 1.2,
                'alpha': 0.05,
                'total_contributions': float(df['contributions'].sum() if 'contributions' in df.columns else 1000000),
                'total_distributions': float(df['distributions'].sum() if 'distributions' in df.columns else 1500000),
                'fund_size': float(df['nav'].max() if 'nav' in df.columns else 1000000)
            }
            
            return {
                'success': True,
                'data': metrics
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cashflow_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract cashflow data for charting.
        
        TODO: Replace this with your existing cashflow processing logic
        """
        try:
            # TODO: Use your existing data processing logic
            df = pd.read_csv(file_path)
            
            # Placeholder implementation - replace with actual logic
            if 'date' not in df.columns:
                df['date'] = pd.date_range(start='2020-01-01', periods=len(df), freq='M')
            
            cashflow_data = []
            for _, row in df.iterrows():
                cashflow_data.append({
                    'date': row['date'].strftime('%Y-%m') if hasattr(row['date'], 'strftime') else str(row['date']),
                    'contributions': float(row.get('contributions', 0)),
                    'distributions': float(row.get('distributions', 0)),
                    'net_cashflow': float(row.get('contributions', 0)) - float(row.get('distributions', 0))
                })
            
            return {
                'success': True,
                'data': cashflow_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def nav_series(self, file_path: str) -> Dict[str, Any]:
        """
        Extract NAV time series data.
        
        TODO: Replace this with your existing NAV processing logic
        """
        try:
            # TODO: Use your existing data processing logic
            df = pd.read_csv(file_path)
            
            # Placeholder implementation - replace with actual logic
            if 'date' not in df.columns:
                df['date'] = pd.date_range(start='2020-01-01', periods=len(df), freq='M')
            
            nav_data = []
            cumulative_nav = 0
            
            for _, row in df.iterrows():
                nav_value = float(row.get('nav', 1000000))
                cumulative_nav += nav_value
                
                nav_data.append({
                    'date': row['date'].strftime('%Y-%m') if hasattr(row['date'], 'strftime') else str(row['date']),
                    'nav': nav_value,
                    'cumulative_nav': cumulative_nav,
                    'benchmark_nav': float(row.get('benchmark_nav', nav_value * 1.1))  # Placeholder
                })
            
            return {
                'success': True,
                'data': nav_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_full_analysis(self, fund_path: str, index_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete PME analysis combining all metrics and data.
        
        TODO: Replace this with your existing full analysis logic from PMEApp
        """
        try:
            # Get individual components
            metrics_result = self.fund_metrics(fund_path)
            cashflow_result = self.cashflow_data(fund_path)
            nav_result = self.nav_series(fund_path)
            
            if not all([metrics_result['success'], cashflow_result['success'], nav_result['success']]):
                return {
                    'success': False,
                    'error': 'Failed to process fund data'
                }
            
            # TODO: If index file provided, incorporate benchmark analysis
            if index_path:
                # benchmark_result = self.process_benchmark(index_path)
                pass
            
            analysis_results = {
                'metrics': metrics_result['data'],
                'cashflow_data': cashflow_result['data'],
                'nav_data': nav_result['data']
            }
            
            self.last_analysis_results = analysis_results
            
            return {
                'success': True,
                'data': analysis_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_supported_file_types(self) -> List[str]:
        """Return list of supported file extensions."""
        return ['.csv', '.xlsx', '.xls']
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate uploaded file format and structure."""
        try:
            if not os.path.exists(file_path):
                return {'valid': False, 'error': 'File not found'}
            
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.get_supported_file_types():
                return {'valid': False, 'error': f'Unsupported file type: {ext}'}
            
            # TODO: Add your existing file validation logic
            # Basic validation - replace with your logic
            if ext == '.csv':
                df = pd.read_csv(file_path, nrows=5)  # Just read first few rows for validation
            else:
                df = pd.read_excel(file_path, nrows=5)
            
            required_columns = ['date']  # TODO: Define your required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    'valid': False, 
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }
            
            return {
                'valid': True,
                'preview': df.to_dict('records')
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
```

### backend/main.py
```python
"""Main entry point for the PME Calculator with pywebview frontend."""

import webview
import os
from pathlib import Path
from api_bridge import ApiBridge

def main():
    """Launch the PME Calculator application with React frontend."""
    
    # Create API bridge instance
    api = ApiBridge()
    
    # Get the frontend build directory
    frontend_dir = Path(__file__).parent.parent / 'frontend' / 'dist'
    
    if not frontend_dir.exists():
        print("Frontend build not found. Please run 'npm run build' in the frontend directory first.")
        return
    
    # Create the main window
    window = webview.create_window(
        title='PME Calculator',
        url=str(frontend_dir / 'index.html'),
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600),
        resizable=True
    )
    
    # Start the webview
    webview.start(debug=False)  # Set to True for development

if __name__ == '__main__':
    main()
```

### backend/requirements.txt
```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
pywebview>=4.4.0
openpyxl>=3.1.0
xlrd>=2.0.0
```

## Frontend Components

### frontend/src/components/FileDrop.tsx
```typescript
import React, { useState, useCallback, useRef } from 'react';
import { Upload, File, X, Check, AlertCircle } from 'lucide-react';

interface FileDropProps {
  onAnalysisComplete: (fundFile: File, indexFile: File | null) => void;
}

interface FileWithPreview extends File {
  preview?: string;
}

const FileDrop: React.FC<FileDropProps> = ({ onAnalysisComplete }) => {
  const [fundFile, setFundFile] = useState<FileWithPreview | null>(null);
  const [indexFile, setIndexFile] = useState<FileWithPreview | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  
  const fundInputRef = useRef<HTMLInputElement>(null);
  const indexInputRef = useRef<HTMLInputElement>(null);
  
  const validateFile = useCallback(async (file: File): Promise<boolean> => {
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx?)$/i)) {
      setValidationMessage('Please upload a CSV or Excel file');
      return false;
    }
    
    if (file.size > maxSize) {
      setValidationMessage('File size must be less than 10MB');
      return false;
    }
    
    setValidationMessage(null);
    return true;
  }, []);
  
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);
  
  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (await validateFile(file)) {
        if (!fundFile) {
          setFundFile(file);
        } else if (!indexFile) {
          setIndexFile(file);
        }
      }
    }
  }, [fundFile, indexFile, validateFile]);
  
  const handleFileInput = useCallback(async (e: React.ChangeEvent<HTMLInputElement>, type: 'fund' | 'index') => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (await validateFile(file)) {
        if (type === 'fund') {
          setFundFile(file);
        } else {
          setIndexFile(file);
        }
      }
    }
  }, [validateFile]);
  
  const removeFile = useCallback((type: 'fund' | 'index') => {
    if (type === 'fund') {
      setFundFile(null);
      if (fundInputRef.current) fundInputRef.current.value = '';
    } else {
      setIndexFile(null);
      if (indexInputRef.current) indexInputRef.current.value = '';
    }
  }, []);
  
  const handleAnalysis = useCallback(async () => {
    if (!fundFile) return;
    
    setUploading(true);
    try {
      await onAnalysisComplete(fundFile, indexFile);
    } finally {
      setUploading(false);
    }
  }, [fundFile, indexFile, onAnalysisComplete]);
  
  const FileDisplay: React.FC<{ file: File; type: string; onRemove: () => void }> = ({ file, type, onRemove }) => (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          <File className="h-5 w-5 text-gray-500 dark:text-gray-400" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {type} File: {file.name}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
      </div>
      <button
        onClick={onRemove}
        className="flex-shrink-0 p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      >
        <X className="h-4 w-4 text-gray-500 dark:text-gray-400" />
      </button>
    </div>
  );
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-gray-700">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Upload Fund Data
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Upload your fund cash flows and optionally a benchmark index file to begin analysis.
        </p>
      </div>
      
      {/* Validation Message */}
      {validationMessage && (
        <div className="mb-4 flex items-center space-x-2 text-red-600 dark:text-red-400">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">{validationMessage}</span>
        </div>
      )}
      
      {/* Drag and Drop Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
        <div className="space-y-2">
          <p className="text-lg font-medium text-gray-900 dark:text-white">
            Drop files here or click to upload
          </p>
          <p className="text-gray-500 dark:text-gray-400">
            Supports CSV, Excel files up to 10MB
          </p>
        </div>
        
        <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Fund Cash Flows (Required)
            </label>
            <input
              ref={fundInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => handleFileInput(e, 'fund')}
              className="block w-full text-sm text-gray-500 dark:text-gray-400
                         file:mr-4 file:py-2 file:px-4
                         file:rounded-lg file:border-0
                         file:text-sm file:font-medium
                         file:bg-blue-50 file:text-blue-700
                         dark:file:bg-blue-900 dark:file:text-blue-300
                         hover:file:bg-blue-100 dark:hover:file:bg-blue-800
                         file:cursor-pointer cursor-pointer"
            />
          </div>
          
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Benchmark Index (Optional)
            </label>
            <input
              ref={indexInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => handleFileInput(e, 'index')}
              className="block w-full text-sm text-gray-500 dark:text-gray-400
                         file:mr-4 file:py-2 file:px-4
                         file:rounded-lg file:border-0
                         file:text-sm file:font-medium
                         file:bg-gray-50 file:text-gray-700
                         dark:file:bg-gray-700 dark:file:text-gray-300
                         hover:file:bg-gray-100 dark:hover:file:bg-gray-600
                         file:cursor-pointer cursor-pointer"
            />
          </div>
        </div>
      </div>
      
      {/* Selected Files Display */}
      <div className="mt-4 space-y-3">
        {fundFile && (
          <FileDisplay 
            file={fundFile} 
            type="Fund" 
            onRemove={() => removeFile('fund')} 
          />
        )}
        
        {indexFile && (
          <FileDisplay 
            file={indexFile} 
            type="Index" 
            onRemove={() => removeFile('index')} 
          />
        )}
      </div>
      
      {/* Analysis Button */}
      {fundFile && (
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleAnalysis}
            disabled={uploading}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
              uploading
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Check className="h-4 w-4" />
                <span>Run PME Analysis</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileDrop;
```

### Next Steps:

1. **Set up the project structure**:
   ```bash
   mkdir pme_calculator
   cd pme_calculator
   mkdir -p backend frontend/src/{components,pages} build
   ```

2. **Copy your existing PME logic**:
   - Copy `pme_app/` folder to the new project root
   - Update the imports in `backend/api_bridge.py` to use your actual functions

3. **Install dependencies**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend  
   cd ../frontend
   npm install
   ```

4. **Build and test**:
   ```bash
   # Build frontend
   cd frontend && npm run build
   
   # Run application
   cd ../backend && python main.py
   ```

The migration preserves all your existing Python analytics while providing a modern, responsive React interface with Glasfunds styling. 