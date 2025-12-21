// MarketML Frontend Configuration
// Auto-configures API URL based on environment - NO MORE HARDCODING!

(function() {
    // Detect environment and set API URL automatically
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    const port = window.location.port;
    
    let API_BASE_URL;
    
    // Check if we're in GitHub Codespaces
    if (hostname.includes('app.github.dev')) {
        // Use SAME origin (port 3000) - we'll use API server that serves frontend
        // This avoids Codespaces auth issues on port 8000
        API_BASE_URL = '';
        console.log('🌐 Codespace detected - using same-origin API');
    }
    // Check if we're on localhost with different ports (development)
    else if (hostname === 'localhost' || hostname === '127.0.0.1') {
        if (port === '3000') {
            // Frontend on 3000, API on 8000
            API_BASE_URL = `${protocol}//localhost:8000`;
        } else {
            // Same origin (API serves frontend)
            API_BASE_URL = '';
        }
    }
    // Production or other environments
    else {
        // Assume same origin (Nginx proxy in production)
        API_BASE_URL = '';
    }
    
    // Export configuration
    window.MARKETML_CONFIG = {
        API_BASE_URL: API_BASE_URL,
        API_VERSION: '/v1',
        get API_URL() {
            return this.API_BASE_URL + this.API_VERSION;
        }
    };
    
    console.log('🔧 MarketML Config Loaded:');
    console.log('  Environment:', hostname.includes('app.github.dev') ? 'Codespace' : 
                                    hostname === 'localhost' ? 'Development' : 'Production');
    console.log('  API URL:', window.MARKETML_CONFIG.API_URL);
    console.log('  No CORS issues - auto-configured! ✅');
})();
