/**
 JWT Token Manager
 Handles storing, retrieving, and sending JWT tokens for API requests
 */

class JWTManager {
    /**
     * Store JWT token
     * @param {string} token - JWT token from login
     */
    static setToken(token) {
        localStorage.setItem('authToken', token);
    }

    /**
     * Get stored JWT token
     * @returns {string|null} JWT token or null if not found
     */
    static getToken() {
        return localStorage.getItem('authToken');
    }

    /**
     * Remove JWT token (logout)
     */
    static removeToken() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} True if token exists
     */
    static isAuthenticated() {
        return !!this.getToken();
    }

    /**
     * Get Authorization header with JWT token
     * @returns {object} Headers object with Authorization header
     */
    static getAuthHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    /**
     * Make authenticated API request
     * @param {string} url - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise} Fetch promise
     */
    static async authenticatedFetch(url, options = {}) {
        const headers = {
            ...this.getAuthHeaders(),
            ...options.headers
        };

        return fetch(url, {
            ...options,
            headers
        });
    }

    /**
     * Parse JWT token to get payload (without verification - for client-side only)
     * @param {string} token - JWT token
     * @returns {object} Token payload
     */
    static parseToken(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(
                atob(base64).split('').map((c) => {
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                }).join('')
            );
            return JSON.parse(jsonPayload);
        } catch (e) {
            console.error('Error parsing token:', e);
            return null;
        }
    }

    /**
     * Check if token is expired
     * @returns {boolean} True if token is expired or doesn't exist
     */
    static isTokenExpired() {
        const token = this.getToken();
        if (!token) return true;

        try {
            const payload = this.parseToken(token);
            if (!payload || !payload.exp) return true;

            const expTime = payload.exp * 1000; // Convert to milliseconds
            return Date.now() >= expTime;
        } catch (e) {
            console.error('Error checking token expiration:', e);
            return true;
        }
    }

    /**
     * Get token expiration time
     * @returns {Date|null} Expiration date or null
     */
    static getTokenExpiration() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const payload = this.parseToken(token);
            if (!payload || !payload.exp) return null;

            return new Date(payload.exp * 1000);
        } catch (e) {
            console.error('Error getting token expiration:', e);
            return null;
        }
    }

    /**
     * Get username from token
     * @returns {string|null} Username or null
     */
    static getUsername() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const payload = this.parseToken(token);
            return payload ? payload.username : null;
        } catch (e) {
            console.error('Error getting username from token:', e);
            return null;
        }
    }
}

// Example usage helper function
async function callAPI(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: JWTManager.getAuthHeaders()
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);

        // If token expired, redirect to login
        if (response.status === 401) {
            console.warn('Unauthorized - Token may have expired');
            JWTManager.removeToken();
            window.location.href = '/';
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}
