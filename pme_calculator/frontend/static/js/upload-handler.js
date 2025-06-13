/**
 * Enhanced file upload handler with comprehensive error handling
 */

class UploadHandler {
    constructor() {
        this.API_BASE = window.API_BASE || 'http://localhost:8000';
    }

    async uploadFile(file) {
        const card = this.addUploadCard(file.name);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.API_BASE}/api/v1/uploads`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                card.setSuccess(result);
                return result;
            } else {
                await this.handleUploadError(response, card);
                return null;
            }
            
        } catch (error) {
            card.setError('Network error – see console for details.');
            console.error('Upload error:', error);
            return null;
        }
    }
    
    async handleUploadError(response, card) {
        """Handle different types of upload errors."""
        const status = response.status;
        
        try {
            const errorData = await response.json();
            const message = errorData.detail || response.statusText;
            
            switch (status) {
                case 409:
                    card.setError('File already exists. Choose a new name or delete the old one.');
                    break;
                case 415:
                    card.setError('Unsupported file type. Please upload CSV or Excel files only.');
                    break;
                case 413:
                    card.setError('File too large (20 MB max). Please compress your file.');
                    break;
                case 500:
                    card.setError(`Server error: ${message}`);
                    break;
                default:
                    card.setError(`Upload failed: ${message}`);
            }
        } catch (e) {
            // If we can't parse the error response
            card.setError(`Upload failed with status ${status}`);
        }
    }
    
    addUploadCard(filename) {
        """Add upload progress card to UI."""
        const card = {
            element: null,
            filename: filename,
            
            setSuccess: function(result) {
                if (this.element) {
                    this.element.classList.add('upload-success');
                    this.element.querySelector('.upload-status').textContent = 'Upload complete';
                    this.element.querySelector('.upload-spinner').style.display = 'none';
                }
            },
            
            setError: function(message) {
                if (this.element) {
                    this.element.classList.add('upload-error');
                    this.element.querySelector('.upload-status').textContent = message;
                    this.element.querySelector('.upload-spinner').style.display = 'none';
                }
            }
        };
        
        // Create card element
        const cardElement = document.createElement('div');
        cardElement.className = 'upload-card';
        cardElement.innerHTML = `
            <div class="upload-filename">${filename}</div>
            <div class="upload-status">Uploading...</div>
            <div class="upload-spinner">⟳</div>
        `;
        
        card.element = cardElement;
        
        // Add to upload area
        const uploadArea = document.querySelector('.upload-area') || document.body;
        uploadArea.appendChild(cardElement);
        
        return card;
    }
}

// Initialize upload handler
const uploadHandler = new UploadHandler();

// Export for use in other scripts
window.uploadHandler = uploadHandler; 