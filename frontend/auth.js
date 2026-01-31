// Authentication utility functions

// Check if user is logged in
function isLoggedIn() {
    return !!localStorage.getItem('access_token');
}

// Get current user info
function getCurrentUser() {
    const userDataStr = localStorage.getItem('user_data');
    if (userDataStr) {
        try {
            return JSON.parse(userDataStr);
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
    
    // Fallback to old method
    return {
        role: localStorage.getItem('user_role'),
        id: localStorage.getItem('user_id'),
        username: localStorage.getItem('username') || 'User',
        first_name: localStorage.getItem('first_name') || '',
        last_name: localStorage.getItem('last_name') || '',
        email: localStorage.getItem('email') || '',
        token: localStorage.getItem('access_token')
    };
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_data');
    localStorage.removeItem('active_club_id');
    localStorage.removeItem('active_club_name');
    localStorage.removeItem('active_club_role');
    localStorage.removeItem('active_club_department');
    window.location.href = '/index.html';
}

// Protect page - redirect to login if not authenticated
function protectPage(requiredRole = null) {
    if (!isLoggedIn()) {
        window.location.href = '/login.html';
        return false;
    }

    const user = getCurrentUser();
    if (requiredRole && user.role !== requiredRole) {
        window.location.href = '/login.html';
        return false;
    }

    return true;
}

// API call with auth header
async function apiCall(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired, clear and redirect to login
        logout();
        return null;
    }

    return response;
}
