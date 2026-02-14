/**
 * CORS Usage Examples
 * Practical examples for using CORS validator and JWT manager
 */
C:\Users\Dell\Documents\AI_Agents_Intensive\projura-agent\static\cors_examples.js
// ============================================================================
// Example 1: Simple API Call with CORS Validation
// ============================================================================

async function example1_basicApiFetch() {
    try {
        // Make request with CORS validation
        const response = await CORSValidator.fetchWithCORS('/api/projects', {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Projects:', data);
        return data;
    } catch (error) {
        console.error('CORS or API error:', error.message);
    }
}


// ============================================================================
// Example 2: Authenticated API Call with JWT
// ============================================================================

async function example2_authenticatedFetch() {
    try {
        // Make authenticated request (includes JWT token)
        const response = await JWTManager.authenticatedFetch('/api/projects', {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        console.log('User projects:', data);
        return data;
    } catch (error) {
        console.error('Authenticated request failed:', error.message);
    }
}


// ============================================================================
// Example 3: POST Request with Data and CORS Validation
// ============================================================================

async function example3_postWithCORS(projectData) {
    try {
        const response = await CORSValidator.fetchWithCORS('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${JWTManager.getToken()}`
            },
            body: JSON.stringify(projectData)
        });

        if (!response.ok) {
            throw new Error(`Failed to create project: ${response.status}`);
        }

        const newProject = await response.json();
        console.log('Created project:', newProject);
        return newProject;
    } catch (error) {
        console.error('Project creation failed:', error.message);
    }
}


// ============================================================================
// Example 4: Using Call API Helper Function
// ============================================================================

async function example4_callAPIHelper() {
    try {
        // Create project using helper function
        const projectData = {
            name: 'My New Project',
            description: 'Project description',
            category: 'web_development'
        };

        // callAPI automatically includes CORS validation and authentication
        const result = await callAPI('/api/projects', 'POST', projectData);

        if (!result) {
            console.log('Request failed or user not authenticated');
            return;
        }

        console.log('Project created:', result);
        return result;
    } catch (error) {
        console.error('Error:', error.message);
    }
}


// ============================================================================
// Example 5: Pre-flight CORS Validation
// ============================================================================

async function example5_validateBeforeRequest(url, method = 'GET') {
    // Validate CORS before making request
    const corsCheck = CORSValidator.validateRequestCORS(url, method);

    console.log('CORS Validation Result:');
    console.log('- Allowed:', corsCheck.allowed);
    console.log('- Cross-Origin:', corsCheck.isCrossOrigin);
    console.log('- Warnings:', corsCheck.warnings);

    if (!corsCheck.allowed) {
        console.error('CORS validation failed - request not allowed');
        return null;
    }

    try {
        const response = await CORSValidator.fetchWithCORS(url, { method });
        return response;
    } catch (error) {
        console.error('Request failed:', error.message);
    }
}


// ============================================================================
// Example 6: Validate Response CORS Headers
// ============================================================================

async function example6_validateResponseHeaders(url) {
    try {
        const response = await CORSValidator.fetchWithCORS(url);

        // Validate CORS headers in response
        const validation = CORSValidator.validateCORSHeaders(response);

        console.log('Response CORS Validation:');
        console.log('- Valid:', validation.valid);
        console.log('- Headers:', validation.headers);
        console.log('- Errors:', validation.errors);

        if (!validation.valid) {
            console.warn('Response CORS validation failed');
        }

        return response;
    } catch (error) {
        console.error('Error:', error.message);
    }
}


// ============================================================================
// Example 7: Debug Mode
// ============================================================================

function example7_debugMode() {
    // Enable debug logging
    CORSValidator.enableDebug();

    console.log('Debug mode enabled. Making test request...');

    // Make a request - will log detailed CORS information
    CORSValidator.fetchWithCORS('/api/projects')
        .then(() => {
            console.log('Request completed. Check logs above.');
            // Disable debug after testing
            CORSValidator.disableDebug();
        })
        .catch(error => {
            console.error('Request failed:', error);
            CORSValidator.disableDebug();
        });
}


// ============================================================================
// Example 8: Login with CORS and JWT
// ============================================================================

async function example8_loginFlow(email, password) {
    try {
        // Send login request
        const response = await CORSValidator.fetchWithCORS('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        const data = await response.json();

        // Store JWT token
        JWTManager.setToken(data.token);
        console.log('Login successful');

        // Now you can make authenticated requests
        const projects = await JWTManager.authenticatedFetch('/api/projects');
        return projects;
    } catch (error) {
        console.error('Login error:', error.message);
    }
}


// ============================================================================
// Example 9: Handle CORS Errors Gracefully
// ============================================================================

async function example9_errorHandling(url) {
    try {
        const response = await CORSValidator.fetchWithCORS(url);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'API error');
        }

        return await response.json();
    } catch (error) {
        if (error.message.includes('CORS')) {
            console.error('CORS Error - origin not allowed');
            alert('Access denied. Check with administrator.');
        } else if (error.message.includes('401')) {
            console.error('Unauthorized - redirecting to login');
            JWTManager.removeToken();
            window.location.href = '/';
        } else {
            console.error('API Error:', error.message);
            alert(`Error: ${error.message}`);
        }
    }
}


// ============================================================================
// Example 10: Check Authentication Status
// ============================================================================

function example10_authStatus() {
    console.log('Authentication Status:');
    console.log('- Authenticated:', JWTManager.isAuthenticated());
    console.log('- Token expired:', JWTManager.isTokenExpired());
    console.log('- Username:', JWTManager.getUsername());
    console.log('- Expiration:', JWTManager.getTokenExpiration());

    if (JWTManager.isTokenExpired()) {
        console.warn('Token expired - user should log in again');
        JWTManager.removeToken();
        window.location.href = '/';
    }
}


// ============================================================================
// Example 11: Cross-Origin Data Transfer
// ============================================================================

async function example11_crossOriginRequest() {
    // This is a cross-origin request example
    // from http://localhost:5000 to https://api.otherdomain.com

    try {
        const corsCheck = CORSValidator.validateRequestCORS(
            'https://api.otherdomain.com/data',
            'GET'
        );

        console.log('Cross-origin validation:');
        console.log('- From:', window.location.origin);
        console.log('- To:', 'https://api.otherdomain.com');
        console.log('- Allowed:', corsCheck.allowed);

        if (corsCheck.allowed) {
            const response = await CORSValidator.fetchWithCORS(
                'https://api.otherdomain.com/data'
            );
            return await response.json();
        } else {
            console.error('Cross-origin request not allowed');
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}


// ============================================================================
// Example 12: Batch Requests with Error Handling
// ============================================================================

async function example12_batchRequests() {
    const endpoints = [
        '/api/projects',
        '/api/statistics',
        '/api/history'
    ];

    try {
        // Make multiple requests in parallel
        const promises = endpoints.map(endpoint =>
            JWTManager.authenticatedFetch(endpoint)
                .then(r => {
                    if (!r.ok) throw new Error(`Failed: ${endpoint}`);
                    return r.json();
                })
                .catch(error => {
                    console.error(`Error for ${endpoint}:`, error);
                    return null;
                })
        );

        const results = await Promise.all(promises);
        console.log('Batch results:', results);
        return results;
    } catch (error) {
        console.error('Batch request error:', error.message);
    }
}


// ============================================================================
// Example 13: Real-world Form Submission
// ============================================================================

async function example13_formSubmission() {
    const form = document.querySelector('#projectForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            name: form.querySelector('#projectName').value,
            description: form.querySelector('#projectDescription').value,
            category: form.querySelector('#projectCategory').value
        };

        try {
            const response = await JWTManager.authenticatedFetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to create project');
            }

            const newProject = await response.json();
            console.log('Project created successfully:', newProject);

            // Reset form and show success
            form.reset();
            alert('Project created successfully!');
        } catch (error) {
            console.error('Form submission error:', error);
            alert(`Error: ${error.message}`);
        }
    });
}


// ============================================================================
// Example 14: Enable Debug and Test
// ============================================================================

function example14_setupDebugAndTest() {
    // Run this in browser console to test the entire CORS system

    console.log('=== CORS & JWT System Test ===');

    // 1. Check if scripts are loaded
    console.log('CORSValidator loaded:', typeof CORSValidator !== 'undefined');
    console.log('JWTManager loaded:', typeof JWTManager !== 'undefined');

    // 2. Enable debug
    CORSValidator.enableDebug();

    // 3. Check auth status
    console.log('Authenticated:', JWTManager.isAuthenticated());

    // 4. Validate request
    const corsCheck = CORSValidator.validateRequestCORS('/api/test', 'GET');
    console.log('CORS check:', corsCheck);

    // 5. Make test request
    return CORSValidator.fetchWithCORS('/api/projects')
        .then(r => {
            console.log('✓ Test request successful');
            CORSValidator.disableDebug();
        })
        .catch(e => {
            console.error('✗ Test request failed:', e.message);
            CORSValidator.disableDebug();
        });
}


// ============================================================================
// Browser Console Quick Commands
// ============================================================================

/*
Copy and paste these into your browser console to test:

// Enable debug
CORSValidator.enableDebug();

// Test basic fetch
CORSValidator.fetchWithCORS('/api/projects').then(r => r.json()).then(console.log);

// Check auth
console.log('Auth:', JWTManager.isAuthenticated());

// Login test
callAPI('/login', 'POST', {email: 'test@example.com', password: 'pass'});

// Disable debug
CORSValidator.disableDebug();
*/

