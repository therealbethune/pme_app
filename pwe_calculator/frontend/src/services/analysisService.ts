interface UploadResponse {
  success: boolean;
  file_id?: string;
  message?: string;
}

interface AnalysisResponse {
  success: boolean;
  detail?: string;
  results?: any;
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
      const response = await fetch('/api/analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fund_id: fundId,
          index_id: indexId,
        }),
      });
      
      return await response.json();
    } catch (error) {
      return {
        success: false,
        detail: 'Analysis failed: ' + (error as Error).message
      };
    }
  }
}; 