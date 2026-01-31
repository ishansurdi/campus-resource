// API Configuration Helper
// This file provides a helper function to get API URLs
// Usage: const url = getApiUrl('/api/auth/login/');

function getApiUrl(path) {
    // Ensure we have the config loaded
    if (typeof window.APP_CONFIG !== 'undefined') {
        return window.APP_CONFIG.getApiUrl(path);
    }
    
    // Fallback: detect environment if config not loaded
    const isLocal = window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1' ||
                    window.location.hostname.includes('localhost');
    
    const baseUrl = isLocal ? 'http://localhost:8000' : 'https://campus-resource-8pw5.onrender.com';
    
    if (!path.startsWith('/')) {
        path = '/' + path;
    }
    
    return baseUrl + path;
}

// Make it available globally
window.getApiUrl = getApiUrl;
