interface FileInfo {
  id: string;
  name: string;
  type: 'fund' | 'index';
}

interface FileStoreState {
  fundFile: FileInfo | null;
  indexFile: FileInfo | null;
  analysisResults: any | null;
}

class FileStore {
  private state: FileStoreState = {
    fundFile: null,
    indexFile: null,
    analysisResults: null,
  };

  getState(): FileStoreState {
    return this.state;
  }

  addFundFile(file: FileInfo): void {
    this.state.fundFile = file;
  }

  addIndexFile(file: FileInfo): void {
    this.state.indexFile = file;
  }

  setAnalysisResults(results: any): void {
    this.state.analysisResults = results;
  }

  clearFiles(): void {
    this.state = {
      fundFile: null,
      indexFile: null,
      analysisResults: null,
    };
  }
}

export const fileStore = new FileStore(); 