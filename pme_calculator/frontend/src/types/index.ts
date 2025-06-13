// Core Data Types
export interface FundData {
  date: string;
  cashflow: number;
  nav: number;
  contributions?: number;
  distributions?: number;
}

export interface IndexData {
  date: string;
  price: number;
  returns?: number;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface FileUploadResponse {
  success: boolean;
  message?: string;
  error?: string;
  data?: {
    rows: number;
    columns: string[];
    date_range: {
      start: string;
      end: string;
    };
  };
}

// Analysis Results
export interface PMEMetrics {
  'Fund IRR': number;
  'TVPI': number;
  'DPI': number;
  'RVPI': number;
  'KS PME'?: number;
  'PME IRR'?: number;
  'Index IRR'?: number;
  'Index TVPI'?: number;
  'Direct Alpha'?: number;
  'Alpha'?: number;
  'Beta'?: number;
  'Fund Volatility'?: number;
  'Index Volatility'?: number;
  'Fund Drawdown'?: number;
  'Index Drawdown'?: number;
  'Fund Best 1Y Return'?: number;
  'Fund Worst 1Y Return'?: number;
  'Index Best 1Y Return'?: number;
  'Index Worst 1Y Return'?: number;
  'Total Contributions': number;
  'Total Distributions': number;
  'Final NAV': number;
  'Method Used': string;
  'Risk Free Rate'?: number;
  'Confidence Level'?: number;
}

export interface CashflowData {
  date: string;
  contributions: number;
  distributions: number;
  net_cashflow: number;
  nav: number;
}

export interface NAVData {
  date: string;
  nav: number;
  cumulative_contributions: number;
  cumulative_distributions: number;
  benchmark_nav?: number;
}

export interface AnalysisResults {
  metrics: PMEMetrics;
  cashflow_data: CashflowData[];
  nav_data: NAVData[];
  has_benchmark: boolean;
  summary?: {
    fund_name: string;
    analysis_date: string;
    data_points: number;
    benchmark_used: boolean;
  };
}

// Component Props Types
export interface KPICardProps {
  metric: number;
  label: string;
  icon: React.ReactNode;
  trend: 'up' | 'down' | 'neutral';
  format?: 'percentage' | 'multiple' | 'currency' | 'number';
  precision?: number;
}

export interface UploadCardProps {
  title: string;
  description: string;
  acceptedFileTypes: string;
  maxFileSize?: number;
  onFileSelect: (file: File) => Promise<void>;
  isUploading?: boolean;
  uploadProgress?: number;
  selectedFile?: File | null;
  onClearFile?: () => void;
  allowedExtensions?: string[];
}

export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
  color?: string;
}

// Application State Types
export interface AppState {
  isDarkMode: boolean;
  isEnhancedMode: boolean;
  isLoading: boolean;
  error: string | null;
  connectionStatus: 'loading' | 'connected' | 'disconnected' | 'demo';
}

// File Validation Types
export interface FileValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  metadata?: {
    fileName: string;
    fileSize: number;
    fileType: string;
    rowCount?: number;
    columnCount?: number;
    dateRange?: {
      start: string;
      end: string;
    };
  };
}

// Configuration Types
export interface PMECalculatorConfig {
  api: {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
  };
  upload: {
    maxFileSize: number;
    allowedTypes: string[];
    chunkSize?: number;
  };
  analysis: {
    defaultRiskFreeRate: number;
    defaultConfidenceLevel: number;
    minDataPoints: number;
  };
  ui: {
    theme: 'light' | 'dark' | 'auto';
    chartColors: string[];
    animations: boolean;
  };
}

// Error Types
export class PMECalculatorError extends Error {
  constructor(
    public message: string,
    public code: string,
    public details?: any
  ) {
    super(message);
    this.name = 'PMECalculatorError';
  }
}

export class ValidationError extends PMECalculatorError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

export class APIError extends PMECalculatorError {
  constructor(message: string, details?: any) {
    super(message, 'API_ERROR', details);
    this.name = 'APIError';
  }
}

// Utility Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
export type FileType = 'csv' | 'xlsx' | 'xls' | 'json' | 'parquet';
export type AnalysisMethod = 'Kaplan Schoar' | 'Modified PME' | 'Direct Alpha';
export type ChartType = 'line' | 'bar' | 'area' | 'waterfall' | 'scatter'; 