// File store service for sharing uploaded files across pages
export interface UploadedFile {
  id: string;
  name: string;
  type: 'fund' | 'index';
}

interface FileStoreState {
  fundFile: UploadedFile | null;
  indexFile: UploadedFile | null;
  analysisResults: any | null;
  lastAnalysisDate: Date | null;
}

class FileStoreService {
  private state: FileStoreState = {
    fundFile: null,
    indexFile: null,
    analysisResults: null,
    lastAnalysisDate: null,
  };

  private listeners: Set<(state: FileStoreState) => void> = new Set();
  
  subscribe(callback: (state: FileStoreState) => void): () => void {
    this.listeners.add(callback);
    callback(this.state); // Immediately call with current state
    return () => this.listeners.delete(callback);
  }

  private notify() {
    this.listeners.forEach(callback => callback(this.state));
  }

  // Fetch files from backend and restore state
  async restoreFilesFromBackend() {
    console.log('FileStore - Starting restoreFilesFromBackend...');
    try {
      const response = await fetch('/api/upload/files');
      console.log('FileStore - API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('FileStore - API response data:', data);
        const files = data.files || {};
        
        // Find the most recent fund and index files based on timestamp in ID
        let mostRecentFund: UploadedFile | null = null;
        let mostRecentIndex: UploadedFile | null = null;
        let latestFundTimestamp = 0;
        let latestIndexTimestamp = 0;
        
        Object.entries(files).forEach(([id, fileInfo]: [string, any]) => {
          // Extract timestamp from file ID (format: fund_TIMESTAMP.DECIMAL or index_TIMESTAMP.DECIMAL)
          const timestampMatch = id.match(/(\d+\.\d+)$/);
          const timestamp = timestampMatch ? parseFloat(timestampMatch[1]) : 0;
          console.log(`FileStore - Processing file ${id}, type: ${fileInfo.type}, timestamp: ${timestamp}`);
          
          if (fileInfo.type === 'fund' && timestamp > latestFundTimestamp) {
            mostRecentFund = {
              id,
              name: fileInfo.filename,
              type: 'fund'
            };
            latestFundTimestamp = timestamp;
            console.log('FileStore - Found newer fund file:', mostRecentFund);
          } else if (fileInfo.type === 'index' && timestamp > latestIndexTimestamp) {
            mostRecentIndex = {
              id,
              name: fileInfo.filename,
              type: 'index'
            };
            latestIndexTimestamp = timestamp;
            console.log('FileStore - Found newer index file:', mostRecentIndex);
          }
        });
        
        // Update state with restored files
        let stateChanged = false;
        if (mostRecentFund) {
          this.state.fundFile = mostRecentFund;
          stateChanged = true;
          console.log('FileStore - Restored fund file from backend:', mostRecentFund);
        }
        if (mostRecentIndex) {
          this.state.indexFile = mostRecentIndex;
          stateChanged = true;
          console.log('FileStore - Restored index file from backend:', mostRecentIndex);
        }
        
        if (stateChanged) {
          console.log('FileStore - State changed, notifying listeners. New state:', this.state);
          this.notify();
        } else {
          console.log('FileStore - No state changes, current state:', this.state);
        }
      } else {
        console.error('FileStore - API response not ok:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('FileStore - Failed to restore files from backend:', error);
    }
  }
  
  addFundFile(file: UploadedFile) {
    console.log('Adding fund file to store:', file);
    this.state.fundFile = file;
    this.notify();
    console.log('File store state after adding fund file:', this.state);
  }

  addIndexFile(file: UploadedFile) {
    console.log('Adding index file to store:', file);
    this.state.indexFile = file;
    this.notify();
    console.log('File store state after adding index file:', this.state);
  }
  
  clearFiles() {
    this.state.fundFile = null;
    this.state.indexFile = null;
    this.state.analysisResults = null;
    this.notify();
  }

  clearFundFile() {
    this.state.fundFile = null;
    this.notify();
  }

  clearIndexFile() {
    this.state.indexFile = null;
    this.notify();
  }

  setAnalysisResults(results: any) {
    this.state.analysisResults = results;
    this.state.lastAnalysisDate = new Date();
    this.notify();
  }

  getState(): FileStoreState {
    return { ...this.state };
  }

  getAnalysisResults() {
    return this.state.analysisResults;
  }
}

export const fileStore = new FileStoreService();
export type { FileStoreState }; 