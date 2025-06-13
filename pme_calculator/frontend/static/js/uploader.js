/**
 * Enhanced uploader with Excel/clipboard paste support
 */

// Import XLSX library for Excel/clipboard processing
import * as XLSX from 'https://cdn.jsdelivr.net/npm/xlsx@0.19.3/+esm';

class EnhancedUploader {
    constructor() {
        this.API_BASE = window.API_BASE || 'http://localhost:8000';
        this.initClipboardListener();
    }

    /**
     * Initialize clipboard paste listener for Excel data
     */
    initClipboardListener() {
        document.addEventListener('paste', e => {
            const htmlData = e.clipboardData.getData('text/html');
            const textData = e.clipboardData.getData('text/plain');
            
            if (htmlData) {
                // Process HTML table data (from Excel)
                this.processClipboardData(htmlData, 'html');
            } else if (textData && textData.includes('\t')) {
                // Process tab-separated data
                this.processClipboardData(textData, 'text');
            }
        });
    }

    /**
     * Process clipboard data and convert to CSV
     */
    processClipboardData(data, type) {
        try {
            let csv;
            
            if (type === 'html') {
                // Parse HTML table data using XLSX
                const wb = XLSX.read(data, { type: 'string' });
                csv = XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);
            } else {
                // Convert tab-separated to CSV
                csv = data.split('\n').map(row => 
                    row.split('\t').map(cell => 
                        cell.includes(',') ? `"${cell}"` : cell
                    ).join(',')
                ).join('\n');
            }
            
            // Create file from CSV data
            const file = new File([csv], 'clipboard.csv', { type: 'text/csv' });
            this.uploadFile(file);
            
            console.log('📋 Clipboard data processed and uploaded');
            
        } catch (error) {
            console.error('Error processing clipboard data:', error);
            this.showNotification('Failed to process clipboard data', 'error');
        }
    }

    /**
     * Upload file with enhanced error handling
     */
    async uploadFile(file) {
        const notification = this.showNotification(`Uploading ${file.name}...`, 'info');
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            // Determine upload endpoint based on file content
            const endpoint = this.detectFileType(file.name);
            
            const response = await fetch(`${this.API_BASE}/api/upload/${endpoint}`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                this.updateNotification(notification, `✅ ${file.name} uploaded successfully`, 'success');
                
                // Trigger file list refresh if function exists
                if (window.refreshFileList) {
                    window.refreshFileList();
                }
                
                return result;
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Upload failed: ${response.status}`);
            }
            
        } catch (error) {
            this.updateNotification(notification, `❌ Upload failed: ${error.message}`, 'error');
            console.error('Upload error:', error);
            return null;
        }
    }

    /**
     * Detect file type for appropriate endpoint
     */
    detectFileType(filename) {
        const lower = filename.toLowerCase();
        if (lower.includes('fund') || lower.includes('cashflow')) {
            return 'fund';
        } else if (lower.includes('index') || lower.includes('benchmark') || lower.includes('market')) {
            return 'index';
        }
        return 'fund'; // Default to fund
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add styles if not already present
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    padding: 12px 16px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    max-width: 400px;
                    animation: slideIn 0.3s ease-out;
                }
                .notification-info { background: #0066cc; color: white; }
                .notification-success { background: #00ff88; color: #000; }
                .notification-error { background: #ff6b6b; color: white; }
                .notification-content { display: flex; justify-content: space-between; align-items: center; }
                .notification-close { 
                    background: none; border: none; color: inherit; 
                    font-size: 18px; cursor: pointer; margin-left: 10px;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
        
        return notification;
    }

    /**
     * Update existing notification
     */
    updateNotification(notification, message, type) {
        if (notification && notification.parentElement) {
            notification.className = `notification notification-${type}`;
            notification.querySelector('.notification-message').textContent = message;
        }
    }

    /**
     * Handle drag and drop files
     */
    handleDrop(event, targetType = 'fund') {
        event.preventDefault();
        const files = Array.from(event.dataTransfer.files);
        
        files.forEach(file => {
            if (this.isValidFileType(file)) {
                this.uploadFile(file);
            } else {
                this.showNotification(`Invalid file type: ${file.name}`, 'error');
            }
        });
    }

    /**
     * Validate file type
     */
    isValidFileType(file) {
        const validTypes = [
            'text/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        return validTypes.includes(file.type) || file.name.toLowerCase().endsWith('.csv');
    }
}

// Initialize enhanced uploader
const enhancedUploader = new EnhancedUploader();

// Export for global use
window.enhancedUploader = enhancedUploader;
window.uploadFile = (file) => enhancedUploader.uploadFile(file);

export default enhancedUploader; 