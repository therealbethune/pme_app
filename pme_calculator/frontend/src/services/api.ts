/**
 * API Service for PME Calculator FastAPI Backend
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface UploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  message: string;
  columns: string[];
}

export interface AnalysisResponse {
  success: boolean;
  request_id?: string;
  metrics: {
    'Fund IRR': number;
    'TVPI': number;
    'DPI': number;
    'RVPI': number;
    'Total Contributions': number;
    'Total Distributions': number;
    'Final NAV': number;
    'PME Ratio'?: number;
    'Index Return'?: number;
    'Alpha'?: number;
    'Index Volatility'?: number;
    [key: string]: number | undefined;
  };
  summary: {
    fund_performance: string;
    vs_benchmark: string;
    risk_profile: string;
  };
  has_benchmark: boolean;
  analysis_date: string;
  chart_data?: {
    waterfall?: Array<any>;
    nav_timeline?: Array<any>;
    cashflow_summary?: any;
    performance_comparison?: any;
    risk_return?: any;
  };
  advanced_analytics?: {
    monte_carlo?: any;
    stress_tests?: any;
    sensitivity?: any;
    advanced_benchmarking?: any;
    risk_analytics?: any;
  };
}

export interface HealthResponse {
  status: string;
  message: string;
  version: string;
}

export class ApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async checkHealth() {
    const response = await this.axiosInstance.get('/api/health');
    return response.data;
  }

  async getPortfolios() {
    const response = await this.axiosInstance.get('/api/portfolios');
    return response.data;
  }

  async getPortfolioAnalytics(portfolioId: string) {
    const response = await this.axiosInstance.get(`/api/portfolio/${portfolioId}/analytics`);
    return response.data;
  }

  async uploadFundFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.axiosInstance.post('/api/upload/fund', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async uploadIndexFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.axiosInstance.post('/api/upload/index', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async runAnalysis() {
    // First get the list of uploaded files to determine IDs
    const filesResponse = await this.axiosInstance.get('/api/upload/files');
    const files = filesResponse.data.files;
    
    if (!files || Object.keys(files).length === 0) {
      throw new Error('No files uploaded. Please upload fund and index files first.');
    }
    
    // Find fund and index file IDs
    let fundFileId = null;
    let indexFileId = null;
    
    for (const [fileId, fileData] of Object.entries(files)) {
      if (fileId.startsWith('fund_')) {
        fundFileId = fileId;
      } else if (fileId.startsWith('index_')) {
        indexFileId = fileId;
      }
    }
    
    if (!fundFileId) {
      throw new Error('No fund file found. Please upload a fund file first.');
    }
    
    // Prepare the analysis request
    const analysisRequest = {
      fund_file_id: fundFileId,
      index_file_id: indexFileId, // Optional, can be null if no benchmark
      method: "Kaplan Schoar", // Default method
      risk_free_rate: 0.02, // 2% default risk-free rate
      confidence_level: 0.95 // 95% confidence level
    };
    
    // Call the real analysis endpoint with actual data processing
    const params = new URLSearchParams({ fund_file_id: fundFileId });
    if (indexFileId) {
      params.append('index_file_id', indexFileId);
    }
    
    const response = await this.axiosInstance.post(`/api/analysis/run-sync?${params.toString()}`);
    return response.data;
  }

  async listUploadedFiles() {
    const response = await this.axiosInstance.get('/api/upload/files');
    return response.data;
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export for potential testing/mocking
export default ApiService; 