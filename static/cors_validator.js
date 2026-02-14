/**
 * CORS (Cross-Origin Resource Sharing) Handler
 * Validates and manages CORS headers in API requests
 */

class CORSValidator {
    /**
     * Allowed origins for validation
     */
    static allowedOrigins = [
        'http://localhost:5000',
        'http://localhost:3000',
        'http://127.0.0.1:5000',
        'http://127.0.0.1:3000',
        window.location.origin,  // Current origin
    ];

    /**
     * Expected CORS headers from server
     */
    static expectedHeaders = [
        'Access-Control-Allow-Origin',
        'Access-Control-Allow-Methods',
        'Access-Control-Allow-Headers',
    ];

    /**
     * Log CORS information for debugging
     * @param {string} message - Debug message
     * @param {object} data - Additional data to log
     */
    static log(message, data = {}) {
        if (localStorage.getItem('CORS_DEBUG_MODE') === 'true') {
            console.log(`[CORS] ${message}`, data);
        }
    }

    /**
     * Validate response origin header
     * @param {Response} response - Fetch response object
     * @returns {boolean} True if origin is valid
     */
    static validateResponseOrigin(response) {
        const origin = response.headers.get('Access-Control-Allow-Origin');

        if (!origin) {
            this.log('No Access-Control-Allow-Origin header found');
            return false;
        }

        // Check if origin matches current request origin
        if (origin === window.location.origin || origin === '*') {
            this.log('Valid origin header:', { origin });
            return true;
        }

        this.log('Invalid origin header:', { origin, expected: window.location.origin });
        return false;
    }

    /**
     * Validate response CORS headers
     * @param {Response} response - Fetch response object
     * @returns {object} Validation result
     */
    static validateCORSHeaders(response) {
        const result = {
            valid: true,
            headers: {},
            errors: []
        };

        // Check all expected CORS headers
        this.expectedHeaders.forEach(header => {
            const value = response.headers.get(header);
            result.headers[header] = value;

            if (!value) {
                result.errors.push(`Missing header: ${header}`);
            }
        });

        // Validate specific headers
        const allowOrigin = response.headers.get('Access-Control-Allow-Origin');
        if (!allowOrigin) {
            result.valid = false;
            result.errors.push('Access-Control-Allow-Origin is required');
        }

        const allowMethods = response.headers.get('Access-Control-Allow-Methods');
        if (!allowMethods) {
            result.errors.push('Access-Control-Allow-Methods is missing');
        }

        if (result.errors.length > 0) {
            result.valid = false;
        }

        this.log('CORS validation result:', result);
        return result;
    }

    /**
     * Get CORS-safe request headers
     * @returns {object} Headers object with safe defaults
     */
    static getCORSHeaders() {
        return {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',  // Helps prevent CSRF
        };
    }

    /**
     * Validate CORS before making request
     * @param {string} url - Request URL
     * @param {string} method - HTTP method
     * @returns {object} Validation result
     */
    static validateRequestCORS(url, method = 'GET') {
        const result = {
            allowed: true,
            url: url,
            method: method,
            warnings: []
        };

        try {
            const reqUrl = new URL(url, window.location.origin);
            const isCrossOrigin = reqUrl.origin !== window.location.origin;

            if (isCrossOrigin) {
                result.isCrossOrigin = true;
                this.log('Cross-origin request detected:', {
                    from: window.location.origin,
                    to: reqUrl.origin
                });

                // For cross-origin, validate against allowed origins
                const isAllowed = this.allowedOrigins.some(origin =>
                    reqUrl.origin === origin || reqUrl.origin === new URL(origin).origin
                );

                if (!isAllowed) {
                    result.allowed = false;
                    result.warnings.push(`Origin ${reqUrl.origin} not in allowed list`);
                }
            } else {
                result.isCrossOrigin = false;
                this.log('Same-origin request');
            }
        } catch (error) {
            result.warnings.push(`URL parsing error: ${error.message}`);
        }

        return result;
    }

    /**
     * Enhanced fetch with CORS validation
     * @param {string} url - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise<Response>} Fetch response
     */
    static async fetchWithCORS(url, options = {}) {
        const method = options.method || 'GET';

        // Validate CORS before request
        const corsCheck = this.validateRequestCORS(url, method);
        if (!corsCheck.allowed) {
            throw new Error(`CORS validation failed: ${corsCheck.warnings.join(', ')}`);
        }

        // Prepare fetch options with CORS headers
        const fetchOptions = {
            ...options,
            method: method,
            headers: {
                ...this.getCORSHeaders(),
                ...options.headers
            },
            // Include credentials for same-origin requests
            credentials: corsCheck.isCrossOrigin ? 'omit' : 'include',
            mode: corsCheck.isCrossOrigin ? 'cors' : 'same-origin',
        };

        this.log('Fetch options:', fetchOptions);

        try {
            const response = await fetch(url, fetchOptions);

            // Validate CORS headers in response
            const corsValidation = this.validateCORSHeaders(response);

            if (!corsValidation.valid) {
                console.warn('[CORS] Validation issues:', corsValidation.errors);
            }

            return response;
        } catch (error) {
            if (error instanceof TypeError && error.message.includes('CORS')) {
                throw new Error(
                    `CORS error: ${error.message}. ` +
                    `Check that backend sends proper CORS headers.`
                );
            }
            throw error;
        }
    }

    /**
     * Enable debug mode for CORS logging
     */
    static enableDebug() {
        localStorage.setItem('CORS_DEBUG_MODE', 'true');
        console.log('[CORS] Debug mode enabled. Use disableDebug() to turn off.');
    }

    /**
     * Disable debug mode
     */
    static disableDebug() {
        localStorage.removeItem('CORS_DEBUG_MODE');
        console.log('[CORS] Debug mode disabled.');
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CORSValidator;
}
