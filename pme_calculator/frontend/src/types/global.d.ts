declare global {
  interface Window {
    pywebview?: {
      api: {
        [key: string]: (...args: any[]) => Promise<any>;
      };
    };
  }
}

export {}; 