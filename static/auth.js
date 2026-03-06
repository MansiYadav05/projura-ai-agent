/**
 * Firebase Authentication Functions
 * Handles user signup, login, email verification, and logout
 * Works with modular Firebase SDK v9+
 */

import {
    auth
} from './firebase.js';

import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    sendEmailVerification,
    applyActionCode,
    checkActionCode,
    currentUser,
    onAuthStateChanged,
    sendPasswordResetEmail,
    updateProfile
} from "https://www.gstatic.com/firebasejs/11.0.1/firebase-auth.js";

/**
 * USER SIGNUP
 * Creates a new user account with email and password
 * Automatically sends verification email
 * 
 * @param {string} email - User's email address
 * @param {string} password - User's password (min 6 characters)
 * @param {string} displayName - User's full name
 * @returns {Promise<{user: Object, message: string}>} - User object and success message
 * @throws {Error} Firebase auth error with code and message
 */
export async function signupUser(email, password, displayName) {
    try {
        console.log('🔐 Signing up user:', email);

        // Validate inputs
        if (!email || !password || !displayName) {
            throw new Error('Email, password, and name are required');
        }

        if (password.length < 6) {
            throw new Error('Password must be at least 6 characters');
        }

        // Create user account
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;

        console.log('✅ User account created:', user.uid);

        // Update user profile with display name
        try {
            await updateProfile(user, {
                displayName: displayName
            });
            console.log('✅ Display name updated:', displayName);
        } catch (profileError) {
            console.warn('⚠️ Could not update display name:', profileError.message);
        }

        // Send email verification
        await sendVerificationEmail(user);

        return {
            user: user,
            message: 'Account created successfully! A verification email has been sent.',
            requiresEmailVerification: true
        };

    } catch (error) {
        console.error('❌ Signup error:', error.code, error.message);
        throw {
            code: error.code,
            message: getFirebaseErrorMessage(error.code),
            originalError: error.message
        };
    }
}

/**
 * USER LOGIN
 * Signs in an existing user with email and password
 * User must have verified email before login
 * 
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<{user: Object, emailVerified: boolean, message: string}>}
 * @throws {Error} Firebase auth error with code and message
 */
export async function loginUser(email, password) {
    try {
        console.log('🔐 Logging in user:', email);

        // Validate inputs
        if (!email || !password) {
            throw new Error('Email and password are required');
        }

        // Sign in user
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;

        console.log('✅ User logged in:', user.uid);

        // Check if email is verified
        if (!user.emailVerified) {
            console.warn('⚠️ Email not verified');
            // Can prompt to resend verification email
            return {
                user: user,
                emailVerified: false,
                message: 'Please verify your email to access the dashboard',
                requiresEmailVerification: true
            };
        }

        return {
            user: user,
            emailVerified: true,
            message: 'Login successful!',
            requiresEmailVerification: false
        };

    } catch (error) {
        console.error('❌ Login error:', error.code, error.message);
        throw {
            code: error.code,
            message: getFirebaseErrorMessage(error.code),
            originalError: error.message
        };
    }
}

/**
 * SEND EMAIL VERIFICATION
 * Sends a verification email to the user
 * Email contains a link to verify the account
 * 
 * @param {Object} user - Firebase user object (optional, uses current user if not provided)
 * @returns {Promise<{message: string}>}
 * @throws {Error} If email cannot be sent
 */
export async function sendVerificationEmail(user) {
    try {
        const targetUser = user || auth.currentUser;

        if (!targetUser) {
            throw new Error('No user found. Please sign up first.');
        }

        // Check if email already verified
        if (targetUser.emailVerified) {
            console.log('ℹ️ Email already verified');
            return {
                message: 'Email already verified',
                alreadyVerified: true
            };
        }

        console.log('📧 Sending verification email to:', targetUser.email);

        // Send verification email
        // Firebase handles the email sending automatically
        await sendEmailVerification(targetUser);

        console.log('✅ Verification email sent');

        return {
            message: `Verification email sent to ${targetUser.email}. Please check your inbox and spam folder.`,
            emailSent: true
        };

    } catch (error) {
        console.error('❌ Email verification error:', error.code, error.message);
        throw {
            code: error.code,
            message: getFirebaseErrorMessage(error.code),
            originalError: error.message
        };
    }
}

/**
 * VERIFY EMAIL WITH CODE
 * Verifies user's email using the code from verification link
 * Called when user clicks the link in verification email
 * 
 * @param {string} code - The verification code from email link
 * @returns {Promise<{verified: boolean, message: string}>}
 * @throws {Error} If code is invalid or expired
 */
export async function verifyEmailWithCode(code) {
    try {
        console.log('🔍 Verifying email with code');

        if (!code) {
            throw new Error('Verification code is required');
        }

        // Check if code is valid
        const codeInfo = await checkActionCode(auth, code);
        console.log('✅ Code is valid');

        // Apply the verification code
        await applyActionCode(auth, code);
        console.log('✅ Email verified');

        return {
            verified: true,
            message: 'Email verified successfully! You can now log in.',
            userEmail: codeInfo.data.email
        };

    } catch (error) {
        console.error('❌ Email verification error:', error.code, error.message);
        throw {
            code: error.code,
            message: getFirebaseErrorMessage(error.code),
            originalError: error.message
        };
    }
}

/**
 * CHECK EMAIL VERIFICATION STATUS
 * Checks if current user's email is verified
 * 
 * @param {Object} user - Firebase user object (optional, uses current user if not provided)
 * @returns {Promise<{verified: boolean, email: string}>}
 */
export async function isEmailVerified(user) {
    try {
        const targetUser = user || auth.currentUser;

        if (!targetUser) {
            return {
                verified: false,
                email: null,
                message: 'No user logged in'
            };
        }

        // Refresh user to get latest verification status
        // Important: After user clicks verification link, status may not update immediately
        await targetUser.reload();

        return {
            verified: targetUser.emailVerified,
            email: targetUser.email,
            displayName: targetUser.displayName,
            uid: targetUser.uid
        };

    } catch (error) {
        console.error('❌ Error checking email verification:', error.message);
        throw {
            code: error.code,
            message: getFirebaseErrorMessage(error.code),
            originalError: error.message
        };
    }
}

/**
 * LOGOUT USER
 * Signs out the current user
 * Clears authentication tokens and local storage if needed
 * 
 * @returns {Promise<{message: string}>}
 * @throws {Error} If logout fails
 */
export async function logoutUser() {
    try {
        console.log('🚪 Logging out user');

        // Sign out from Firebase
        await signOut(auth);

        console.log('✅ User logged out');

        // Optional: Clear JWT token from localStorage if using with backend
        localStorage.removeItem('jwt_token');
        sessionStorage.clear();

        return {
            message: 'Logged out successfully',
            loggedOut: true
        };

    } catch (error) {
        console.error('❌ Logout error:', error.message);
        throw {
            code: error.code,
            message: 'Failed to logout. Please try again.',
            originalError: error.message
        };
    }
}

/**
 * GET CURRENT USER
 * Returns the currently authenticated user
 * 
 * @returns {Promise<{user: Object|null, authenticated: boolean}>}
 */
export async function getCurrentUser() {
    return new Promise((resolve) => {
        onAuthStateChanged(auth, (user) => {
            if (user) {
                console.log('👤 Current user:', user.email);
                resolve({
                    user: user,
                    authenticated: true,
                    email: user.email,
                    emailVerified: user.emailVerified,
                    displayName: user.displayName,
                    uid: user.uid
                });
            } else {
                console.log('ℹ️ No user authenticated');
                resolve({
                    user: null,
                    authenticated: false
                });
            }
        });
    });
}

/**
 * SEND PASSWORD RESET EMAIL
 * Sends password reset link to user's email
 * 
 * @param {string} email - User's email address
 * @returns {Promise<{message: string}>}
 * @throws {Error} If email not found or other error
 */
export async function sendPasswordReset(email) {
    try {
        console.log('📧 Sending password reset email to:', email);

        if (!email) {
            throw new Error('Email is required');
        }

        await sendPasswordResetEmail(auth, email);

        console.log('✅ Password reset email sent');

        return {
            message: `Password reset email sent to ${email}. Check your inbox and spam folder.`,
            emailSent: true
        };

    } catch (error) {
        console.error('❌ Password reset error:', error.code, error.message);
        throw {
            code: error.code,
            message: getFirebaseErrorMessage(error.code),
            originalError: error.message
        };
    }
}

/**
 * HELPER FUNCTION: Map Firebase error codes to user-friendly messages
 * 
 * @param {string} errorCode - Firebase error code
 * @returns {string} - User-friendly error message
 */
function getFirebaseErrorMessage(errorCode) {
    const errorMessages = {
        'auth/invalid-email': 'Invalid email address. Please check and try again.',
        'auth/user-disabled': 'This account has been disabled. Please contact support.',
        'auth/user-not-found': 'No account found with this email. Please sign up first.',
        'auth/wrong-password': 'Incorrect password. Please try again.',
        'auth/email-already-in-use': 'This email is already registered. Please log in or use a different email.',
        'auth/weak-password': 'Password is too weak. Use at least 6 characters.',
        'auth/operation-not-allowed': 'Email/Password login is currently disabled. Try again later.',
        'auth/too-many-requests': 'Too many login attempts. Please try again later.',
        'auth/invalid-action-code': 'Invalid or expired verification code. Please request a new one.',
        'auth/expired-action-code': 'Verification code has expired. Please request a new one.',
        'auth/account-exists-with-different-credential': 'An account already exists with this email.',
        'auth/unknown': 'An unexpected error occurred. Please try again.'
    };

    return errorMessages[errorCode] || errorMessages['auth/unknown'];
}

/**
 * EXPORT ALL FUNCTIONS
 */
export {
    auth,
    onAuthStateChanged,
    getCurrentUser
};

/**
 * USAGE EXAMPLES
 * ===============
 * 
 * // Signup
 * import { signupUser } from './auth.js';
 * 
 * try {
 *   const result = await signupUser('user@example.com', 'password123', 'John Doe');
 *   console.log(result.message);
 *   // Redirect to verify email page
 * } catch (error) {
 *   console.error(error.message);
 * }
 * 
 * // Login
 * import { loginUser } from './auth.js';
 * 
 * try {
 *   const result = await loginUser('user@example.com', 'password123');
 *   if (result.emailVerified) {
 *     // Redirect to dashboard
 *   } else {
 *     // Show verify email message
 *   }
 * } catch (error) {
 *   console.error(error.message);
 * }
 * 
 * // Check current user
 * import { getCurrentUser } from './auth.js';
 * 
 * const { user, authenticated } = await getCurrentUser();
 * if (authenticated) {
 *   console.log('Logged in as:', user.email);
 * }
 */
