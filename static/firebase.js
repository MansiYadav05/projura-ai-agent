/**
 * Firebase Configuration & Initialization
 * Firebase SDK v9+ (Modular SDK)
 */

import { initializeApp , getApps, getApp} from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";
import {
    getAuth,
    setPersistence,
    browserLocalPersistence
} from "https://www.gstatic.com/firebasejs/11.0.1/firebase-auth.js";


const firebaseConfig = {
  apiKey: "AIzaSyAtoBPb_TpflYzRAsfMB3wTsKYXoPDmb9U",
  authDomain: "projura-agent.firebaseapp.com",
  projectId: "projura-agent",
  storageBucket: "projura-agent.firebasestorage.app",
  messagingSenderId: "170531364182",
  appId: "1:170531364182:web:2328d5867f9bd9e7238af7",
  measurementId: "G-4MH9017V52"
};


if (typeof window !== 'undefined' && window.firebaseConfig) {
    Object.assign(firebaseConfig, window.firebaseConfig);
}

// Validate configuration
function validateFirebaseConfig() {
    const requiredKeys = ['apiKey', 'authDomain', 'projectId', 'appId'];
    const missingKeys = requiredKeys.filter(key => !firebaseConfig[key] || firebaseConfig[key].includes('YOUR_'));

    if (missingKeys.length > 0) {
        console.error('❌ Firebase Configuration Error');
        console.error('Missing or incomplete Firebase configuration keys:', missingKeys);
        console.error('Please update the firebaseConfig object with your Firebase project credentials.');
        throw new Error('Invalid Firebase Configuration');
    }
}

// Initialize Firebase
let app;
let auth;

try {
    validateFirebaseConfig();

    // Initialize Firebase App
    app = !getApps().length
  ? initializeApp(firebaseConfig)
  : getApp();

    // Initialize Firebase Authentication
    auth = getAuth(app);

    // Note: Analytics disabled - getAnalytics not imported
    // If you need analytics, import it: import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-analytics.js";
    // const analytics = getAnalytics(app);

    // Enable persistent authentication
    // Users stay logged in even after browser closes
    setPersistence(auth, browserLocalPersistence)
        .then(() => {
            console.log('✅ Firebase initialized successfully');
            console.log('✅ Local persistence enabled (users stay logged in)');
        })
        .catch((error) => {
            console.error('⚠️ Persistence error:', error.message);
        });
} catch (error) {
    console.error('❌ Firebase Initialization Error:', error.message);
    alert('Firebase configuration is incomplete. Please check the console for details.');
}

/**
 * Export Firebase modules for use in other files
 */
export { app, auth, firebaseConfig };

/**
 * Firebase Configuration Guide
 * 1. CREATE FIREBASE PROJECT
 *    - Go to https://console.firebase.google.com
 *    - Click "Create a new project"
 *
 * 2. GET CONFIGURATION CREDENTIALS
 *    - Go to Project Settings (gear icon)
 *    - Click "Your apps" tab
 *    - Click "Add app" > Web
 *    - Copy your config object
 *
 * 3. UPDATE AUTHORIZATION DOMAIN (IMPORTANT FOR RENDER)
 *    - Go to Authentication > Settings
 *    - Copy exact domain from your Render deployment
 *    - Add it to "Authorized domains"
 *    - Example: your-app-name.onrender.com
 *
 * 4. ENABLE EMAIL/PASSWORD AUTH
 *    - Go to Authentication > Sign-in method
 *    - Enable "Email/Password"
 *    - Save
 *
 * 5. ENABLE EMAIL VERIFICATION
 *    - Go to Authentication > Templates
 *    - Customize email verification template (optional)
 *    - Default template is fine for development
 *
 * 6. (OPTIONAL) CONFIGURE CUSTOM DOMAIN
 *    - Go to Authentication > Settings
 *    - Set custom domain for email links
 *    - Useful for white-labeling
 *
 * ENVIRONMENT-SPECIFIC SETUP
 * ==========================
 *
 * LOCAL DEVELOPMENT:
 * - Update firebaseConfig directly in this file
 * - Test email sending in development mode
 *
 * RENDER PRODUCTION:
 * - Set environment variables in Render Dashboard
 * - In Render Dashboard > Environment:
 *   FIREBASE_API_KEY
 *   FIREBASE_AUTH_DOMAIN
 *   FIREBASE_PROJECT_ID
 *   FIREBASE_APP_ID
 *
 * - Script will load from window.firebaseConfig if available
 */

// Import the functions you need from the SDKs you need
// import { initializeApp } from "firebase/app";
// import { getAnalytics } from "firebase/analytics";
// // TODO: Add SDKs for Firebase products that you want to use
// // https://firebase.google.com/docs/web/setup#available-libraries

// // Your web app's Firebase configuration
// // For Firebase JS SDK v7.20.0 and later, measurementId is optional
// const firebaseConfig = {
//   apiKey: "AIzaSyAtoBPb_TpflYzRAsfMB3wTsKYXoPDmb9U",
//   authDomain: "projura-agent.firebaseapp.com",
//   projectId: "projura-agent",
//   storageBucket: "projura-agent.firebasestorage.app",
//   messagingSenderId: "170531364182",
//   appId: "1:170531364182:web:2328d5867f9bd9e7238af7",
//   measurementId: "G-4MH9017V52"
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);
