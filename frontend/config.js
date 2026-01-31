// Configuration for API endpoints
// This file determines whether to use local or production backend

const CONFIG = {
    // Detect environment based on hostname
    isDevelopment: window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' ||
                   window.location.hostname.includes('localhost'),
    
    // API URLs
    API_URL: (function() {
        // Check if running locally
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1' ||
            window.location.hostname.includes('localhost')) {
            return 'http://localhost:8000';
        }
        // Production - deployed on Render
        return 'https://campus-resource-8pw5.onrender.com';
    })(),
    
    // Get full API endpoint
    getApiUrl: function(path) {
        // Ensure path starts with /
        if (!path.startsWith('/')) {
            path = '/' + path;
        }
        return this.API_URL + path;
    }
};

// Make CONFIG available globally
window.APP_CONFIG = CONFIG;

// Log current configuration (useful for debugging)
console.log('App Config:', {
    environment: CONFIG.isDevelopment ? 'Development' : 'Production',
    apiUrl: CONFIG.API_URL
});
