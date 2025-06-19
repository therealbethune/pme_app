interface UploadResponse {
  success: boolean;
  file_id?: string;
  message?: string;
}

interface AnalysisResponse {
  success: boolean;
  detail?: string;
  results?: any;
  metrics?: any;
  charts?: any;
  summary?: any;
  request_id?: string;
  processing_time_ms?: number;
}

interface ComprehensiveAnalysisResponse {
  success: boolean;
  analysis_id?: string;
  metrics?: any;
  charts?: any;
  summary?: any;
  error?: string;
}

interface MetricsResponse {
  data: any[];
  layout: any;
}

export const analysisService = {
  uploadFile: async (file: File, type: 'fund' | 'index'): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      return await response.json();
    } catch (error) {
      return {
        success: false,
        message: 'Upload failed: ' + (error as Error).message
      };
    }
  },

  runAnalysis: async (fundId: string, indexId?: string): Promise<AnalysisResponse> => {
    try {
      const response = await fetch('/api/v1/analysis/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fund_file_id: fundId,
          index_file_id: indexId,
          method: 'kaplan_schoar',
          risk_free_rate: 0.02,
          confidence_level: 0.95
        }),
      });
      
      return await response.json();
    } catch (error) {
      return {
        success: false,
        detail: 'Analysis failed: ' + (error as Error).message
      };
    }
  },

  runSimpleAnalysis: async (): Promise<AnalysisResponse> => {
    try {
      const response = await fetch('/api/v1/analysis/run-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      return await response.json();
    } catch (error) {
      return {
        success: false,
        detail: 'Simple analysis failed: ' + (error as Error).message
      };
    }
  },

  runComprehensiveAnalysis: async (
    fundFileId: string, 
    benchmarkFileId?: string,
    analysisName: string = 'PME Analysis',
    riskFreeRate: number = 0.025,
    includeCharts: boolean = true,
    includeMonteCarlo: boolean = false
  ): Promise<ComprehensiveAnalysisResponse> => {
    try {
      const formData = new FormData();
      formData.append('fund_file_id', fundFileId);
      if (benchmarkFileId) formData.append('benchmark_file_id', benchmarkFileId);
      formData.append('analysis_name', analysisName);
      formData.append('risk_free_rate', riskFreeRate.toString());
      formData.append('include_charts', includeCharts.toString());
      formData.append('include_monte_carlo', includeMonteCarlo.toString());

      const response = await fetch('/api/v1/analysis/run-comprehensive-analysis', {
        method: 'POST',
        body: formData,
      });
      
      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: 'Comprehensive analysis failed: ' + (error as Error).message
      };
    }
  },

  getTWRvsIndex: async (filters?: any): Promise<MetricsResponse> => {
    try {
      const queryParams = new URLSearchParams();
      if (filters?.fund) queryParams.append('fund', filters.fund);
      if (filters?.vintage) queryParams.append('vintage', filters.vintage);
      if (filters?.currency) queryParams.append('currency', filters.currency);

      const response = await fetch(`/v1/metrics/twr_vs_index?${queryParams}`, {
        method: 'GET',
      });
      
      return await response.json();
    } catch (error) {
      throw new Error('Failed to fetch TWR vs Index data: ' + (error as Error).message);
    }
  },

  getAnalysisStatus: async (fileId: string): Promise<any> => {
    try {
      const response = await fetch(`/api/v1/analysis/analysis-status/${fileId}`, {
        method: 'GET',
      });
      
      return await response.json();
    } catch (error) {
      throw new Error('Failed to get analysis status: ' + (error as Error).message);
    }
  },

  exportCharts: async (fileId: string, format: string = 'json', chartTypes?: string): Promise<any> => {
    try {
      const queryParams = new URLSearchParams();
      queryParams.append('format', format);
      if (chartTypes) queryParams.append('chart_types', chartTypes);

      const response = await fetch(`/api/v1/analysis/export-charts/${fileId}?${queryParams}`, {
        method: 'GET',
      });
      
      return await response.json();
    } catch (error) {
      throw new Error('Failed to export charts: ' + (error as Error).message);
    }
  },

  calculateScenarioAnalysis: async (fundFileId: string, scenarios: any[]): Promise<any> => {
    try {
      const formData = new FormData();
      formData.append('fund_file_id', fundFileId);
      formData.append('scenarios', JSON.stringify(scenarios));

      const response = await fetch('/api/v1/analysis/calculate-scenario-analysis', {
        method: 'POST',
        body: formData,
      });
      
      return await response.json();
    } catch (error) {
      throw new Error('Failed to calculate scenario analysis: ' + (error as Error).message);
    }
  },

  getCacheStats: async (): Promise<any> => {
    try {
      const response = await fetch('/api/v1/analysis/cache/stats', {
        method: 'GET',
      });
      
      return await response.json();
    } catch (error) {
      throw new Error('Failed to get cache stats: ' + (error as Error).message);
    }
  },

  clearCache: async (): Promise<any> => {
    try {
      const response = await fetch('/api/v1/analysis/cache/clear', {
        method: 'DELETE',
      });
      
      return await response.json();
    } catch (error) {
      throw new Error('Failed to clear cache: ' + (error as Error).message);
    }
  }
}; 