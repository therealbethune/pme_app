export const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    return (
      import.meta.env.VITE_API_BASE ||
      (window as any).API_BASE ||
      `${window.location.protocol}//${window.location.hostname}:8000`
    );
  } else {
    return (
      process.env.VITE_API_BASE ||
      'http://localhost:8000'
    );
  }
}; 