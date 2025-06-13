const API_BASE_URL = 'http://localhost:8000/api';

class AnalysisService {
  async uploadFile(file: File, type: 'fund' | 'index'): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const endpoint = type === 'fund' ? '/upload/fund' : '/upload/index';

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error during file upload.' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async runAnalysis(fundFileId: string, indexFileId?: string): Promise<any> {
    const params = new URLSearchParams({ fund_file_id: fundFileId });
    if (indexFileId) {
      params.append('index_file_id', indexFileId);
    }

    const response = await fetch(`${API_BASE_URL}/analysis/run-sync?${params.toString()}`, {
      method: 'POST',
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error during analysis.' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const analysisService = new AnalysisService(); 