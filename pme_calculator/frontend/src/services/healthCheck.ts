import { apiService } from './api';

class HealthCheckService {
  private isConnected: boolean = false;
  private lastCheckTime: number = 0;
  private checkInterval: number = 60000; // 1 minute
  private subscribers: Set<(status: boolean) => void> = new Set();
  private checkPromise: Promise<boolean> | null = null;

  constructor() {
    // Initial check
    this.performCheck();
  }

  /**
   * Subscribe to health status changes
   */
  subscribe(callback: (status: boolean) => void): () => void {
    this.subscribers.add(callback);
    
    // Immediately notify with current status
    callback(this.isConnected);
    
    // Return unsubscribe function
    return () => {
      this.subscribers.delete(callback);
    };
  }

  /**
   * Get current connection status
   */
  getStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Force a health check (with debouncing)
   */
  async checkNow(): Promise<boolean> {
    const now = Date.now();
    
    // If we've checked recently, return cached result
    if (now - this.lastCheckTime < 5000) { // 5 second debounce
      return this.isConnected;
    }
    
    // If a check is already in progress, wait for it
    if (this.checkPromise) {
      return this.checkPromise;
    }
    
    return this.performCheck();
  }

  /**
   * Start periodic health checks
   */
  startPeriodicChecks(): void {
    this.stopPeriodicChecks();
    
    setInterval(() => {
      this.performCheck();
    }, this.checkInterval);
  }

  /**
   * Stop periodic health checks
   */
  stopPeriodicChecks(): void {
    // Clear any existing intervals (handled by React cleanup)
  }

  /**
   * Perform the actual health check
   */
  private async performCheck(): Promise<boolean> {
    this.checkPromise = this._doHealthCheck();
    const result = await this.checkPromise;
    this.checkPromise = null;
    return result;
  }

  private async _doHealthCheck(): Promise<boolean> {
    try {
      await apiService.checkHealth();
      this.updateStatus(true);
      this.lastCheckTime = Date.now();
      return true;
    } catch (error) {
      this.updateStatus(false);
      this.lastCheckTime = Date.now();
      return false;
    }
  }

  /**
   * Update status and notify subscribers
   */
  private updateStatus(status: boolean): void {
    if (status !== this.isConnected) {
      this.isConnected = status;
      
      // Notify all subscribers
      this.subscribers.forEach(callback => {
        try {
          callback(status);
        } catch (error) {
          console.error('Error in health check subscriber:', error);
        }
      });
    }
  }
}

// Export singleton instance
export const healthCheckService = new HealthCheckService(); 