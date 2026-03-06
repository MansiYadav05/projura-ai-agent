# Firebase Authentication Integration Guide

Complete guide for integrating Firebase Authentication with email verification for Projura Agent on both local development and Render deployment.

## Table of Contents
1. [Firebase Setup](#firebase-setup)
2. [Project Configuration](#project-configuration)
3. [Local Development Setup](#local-development-setup)
4. [Render Deployment Setup](#render-deployment-setup)
5. [HTML Integration](#html-integration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Firebase Setup

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Create a new project"**
3. Enter project name: `projura-agent` (or your preferred name)
4. Disable Google Analytics (can enable later)
5. Click **"Create Project"**
6. Wait for project to be created and click **"Continue"**

### Step 2: Register Web App

1. In Firebase Console, click the **"Web"** icon (</> symbol)
2. App nickname: `projura-web`
3. Check **"Also set up Firebase Hosting"** (optional)
4. Click **"Register app"**
5. You'll see your Firebase config - **COPY THIS** and save it

Your config will look like:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  authDomain: "projura-agent-xxxxx.firebaseapp.com",
  projectId: "projura-agent-xxxxx",
  storageBucket: "projura-agent-xxxxx.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456ghi789jk"
};
```

### Step 3: Enable Email/Password Authentication

1. In Firebase Console, go to **Authentication** (left sidebar)
2. Click **"Sign-in method"** tab
3. Click **"Email/Password"** provider
4. Toggle **"Enable"**
5. For email link sign-in: keep it **disabled** (not needed)
6. Click **"Save"**

### Step 4: Enable Email Verification

1. In Firebase Console, go to **Authentication** > **Templates**
2. Look for **"Email verification"** template
3. Preview the default template (it's fine as-is)
4. You can customize if needed (optional)
5. Default template is sufficient for most cases

### Step 5: Configure Authorized Domains

**FOR LOCAL DEVELOPMENT:**
1. Go to **Authentication** > **Settings**
2. Scroll to **"Authorized domains"**
3. **`localhost`** is already automatically added ✅
4. **`127.0.0.1`** will also work

**FOR RENDER DEPLOYMENT:**
1. Deploy your app to Render first (see [Render Deployment Setup](#render-deployment-setup) below)
2. Get your Render domain: `your-app-name.onrender.com`
3. Return to Firebase Console > **Authentication** > **Settings**
4. Click **"Add domain"** under "Authorized domains"
5. Enter exactly: `your-app-name.onrender.com` (without https://)
6. Click **"Add"**

**Example:**
```
Authorized domains:
- localhost ✅
- 127.0.0.1 ✅
- my-projura-app.onrender.com (for production)
```

---

## Project Configuration

### For Local Development

**File: `static/firebase.js`**

1. Open `static/firebase.js`
2. Replace the placeholder values with your Firebase config:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",                    // From Firebase Console
  authDomain: "your-project.firebaseapp.com",     // From Firebase Console
  projectId: "your-project-id",                   // From Firebase Console
  storageBucket: "your-project.appspot.com",      // From Firebase Console
  messagingSenderId: "123456789012",              // From Firebase Console
  appId: "1:123456789012:web:abc123def456"       // From Firebase Console
};
```

3. Save the file

### For Render Production

**Option A: Using Environment Variables (Recommended)**

1. In your Render Dashboard:
   - Go to your service
   - Click **"Environment"**
   - Add these environment variables:

```
FIREBASE_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FIREBASE_AUTH_DOMAIN=projura-agent-xxxxx.firebaseapp.com
FIREBASE_PROJECT_ID=projura-agent-xxxxx
FIREBASE_APP_ID=1:123456789012:web:abc123def456ghi789jk
FIREBASE_STORAGE_BUCKET=projura-agent-xxxxx.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789012
```

2. In your Flask app (optional - for server-side usage):
   - Add to `api/index.py`:

```python
import os

firebase_config = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'appId': os.getenv('FIREBASE_APP_ID'),
}
```

**Option B: Update firebase.js directly**

If you prefer not to use environment variables:
1. Update `static/firebase.js` with production credentials
2. Commit to Git (note: this is public data, so it's safe)

---

## Local Development Setup

### Prerequisites
- Node.js installed (for local testing)
- Python 3.8+
- Firebase project created

### Steps

1. **Update firebase.js with your credentials**
   ```bash
   cd projura-agent/static
   # Edit firebase.js and replace placeholder values
   ```

2. **Start Flask development server**
   ```bash
   cd projura-agent
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python api/index.py
   ```

3. **Access the application**
   ```
   http://localhost:5000
   ```

4. **Test signup**
   - Go to http://localhost:5000/signup
   - Fill in email, password, name
   - Click "Sign Up"
   - You should see: "Account created! Check your email for verification."

5. **Verify email**
   - Check your email inbox (Firebase sends from `noreply@firebase.com`)
   - Click the verification link
   - You should be redirected to verify page
   - Or go to http://localhost:5000/verify_email

6. **Test login**
   - Go to http://localhost:5000/login
   - Enter email and password
   - You should see success message
   - Should be redirected to dashboard

### Testing Email in Local Development

Firebase sends real emails in development. Check:
1. Your inbox: `your.email@gmail.com`
2. Spam/Promotions folder
3. If not received:
   - Wait a few seconds (Firebase has slight delay)
   - Check that your email address is correct
   - Verify Firebase Authentication is enabled

---

## Render Deployment Setup

### Step 1: Prepare Application

1. Create `.env.render` file in project root:
```env
GOOGLE_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secret_key
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_APP_ID=your-app-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-messaging-id
ENVIRONMENT=production
FRONTEND_URL=https://your-app-name.onrender.com
```

2. Don't commit `.env.render` to Git (already in .gitignore)

### Step 2: Deploy to Render

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New"** > **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name**: `projura-agent`
   - **Environment**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api/index.py`
   - **Plan**: Free (or higher if needed)

6. Under **Environment**, add all environment variables from `.env.render`

7. Click **"Create Web Service"**
8. Wait for deployment to complete
9. Get your domain: `https://your-app-name.onrender.com`

### Step 3: Add Authorized Domain to Firebase

**IMPORTANT - Do this before testing!**

1. In Firebase Console:
   - Go to **Authentication** > **Settings**
   - Find **"Authorized domains"**
   - Click **"Add domain"**
   - Enter your Render domain (without https://): `your-app-name.onrender.com`
   - Click **"Add"**

2. Wait 5-10 minutes for Firebase to propagate

### Step 4: Update Email Verification Links (Optional)

By default, Firebase email verification links use:
```
https://your-project.firebaseapp.com/...
```

To use your custom domain (your Render domain):
1. Go to **Authentication** > **Settings**
2. Under **"Authorized domains"**, click **"Custom domain"** (if available)
3. Configure your custom domain: `your-app-name.onrender.com`

If custom domain option is not available:
- Keep using default Firebase domain (it will redirect to your app after verification)

### Step 5: Test Production Deployment

```
https://your-app-name.onrender.com/signup
```

Try the full signup → verify → login flow

---

## HTML Integration

### Signup Page Integration

**File: `templates/signup.html`**

Add these script imports before closing `</body>`:

```html
<!-- Firebase Initialization -->
<script src="static/firebase.js" type="module"></script>

<!-- Firebase Authentication Functions -->
<script type="module">
  import { signupUser, sendPasswordReset } from './static/auth.js';
  
  const form = document.getElementById('signupForm');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const nameInput = document.getElementById('name');
  const signupBtn = document.getElementById('signupBtn');
  const alertDiv = document.getElementById('alert');
  const loadingDiv = document.getElementById('loading');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const name = nameInput.value.trim();
    
    try {
      signupBtn.disabled = true;
      loadingDiv.style.display = 'block';
      
      const result = await signupUser(email, password, name);
      
      // Show success message
      alertDiv.textContent = result.message;
      alertDiv.className = 'alert alert-success show';
      
      // Redirect to verify email page after 2 seconds
      setTimeout(() => {
        window.location.href = '/verify_email';
      }, 2000);
      
    } catch (error) {
      console.error('Signup error:', error);
      alertDiv.textContent = error.message || 'Signup failed. Please try again.';
      alertDiv.className = 'alert alert-danger show';
      
      signupBtn.disabled = false;
      loadingDiv.style.display = 'none';
    }
  });
</script>
```

### Login Page Integration

**File: `templates/login.html`**

Add these script imports before closing `</body>`:

```html
<!-- Firebase Initialization -->
<script src="static/firebase.js" type="module"></script>

<!-- Firebase Authentication Functions -->
<script type="module">
  import { loginUser, getCurrentUser } from './static/auth.js';
  
  const form = document.getElementById('login-form');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const loginBtn = document.getElementById('login-btn');
  const errorDiv = document.getElementById('error-message');
  const successDiv = document.getElementById('success-message');

  // Check if already logged in
  window.addEventListener('DOMContentLoaded', async () => {
    const { authenticated, user } = await getCurrentUser();
    if (authenticated && user.emailVerified) {
      window.location.href = '/dashboard';
    }
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    
    try {
      loginBtn.disabled = true;
      errorDiv.style.display = 'none';
      
      const result = await loginUser(email, password);
      
      if (result.emailVerified) {
        successDiv.textContent = result.message;
        successDiv.style.display = 'block';
        
        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 2000);
      } else {
        errorDiv.textContent = 'Please verify your email before login. Redirecting...';
        errorDiv.style.display = 'block';
        
        // Redirect to verify email page
        setTimeout(() => {
          window.location.href = '/verify_email';
        }, 2000);
      }
      
    } catch (error) {
      console.error('Login error:', error);
      errorDiv.textContent = error.message || 'Login failed. Please try again.';
      errorDiv.style.display = 'block';
      
      loginBtn.disabled = false;
    }
  });
</script>
```

### Email Verification Page Integration

**File: `templates/verify_email.html`**

Add these script imports before closing `</body>`:

```html
<!-- Firebase Initialization -->
<script src="static/firebase.js" type="module"></script>

<!-- Firebase Authentication Functions -->
<script type="module">
  import { verifyEmailWithCode, getCurrentUser, sendVerificationEmail, isEmailVerified } from './static/auth.js';
  
  const form = document.getElementById('verifyForm');
  const codeInput = document.getElementById('codeInput');
  const verifyBtn = document.getElementById('verifyBtn');
  const resendBtn = document.getElementById('resendBtn');
  const alertDiv = document.getElementById('alert');
  const loadingDiv = document.getElementById('loading');

  // Check current user email
  window.addEventListener('DOMContentLoaded', async () => {
    try {
      const { user, authenticated } = await getCurrentUser();
      const emailInfo = document.getElementById('emailInfo');
      
      if (authenticated && user.email) {
        emailInfo.textContent = `Email: ${user.email}`;
        
        // Check if already verified
        if (user.emailVerified) {
          alertDiv.textContent = 'Your email is already verified! Redirecting to dashboard...';
          alertDiv.className = 'alert alert-success show';
          
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 2000);
        }
      } else {
        emailInfo.textContent = 'Not logged in. Please sign up first.';
      }
    } catch (error) {
      console.error('Error:', error);
    }
  });

  // Verify email with code
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const code = codeInput.value.trim();
    
    try {
      verifyBtn.disabled = true;
      loadingDiv.style.display = 'block';
      
      const result = await verifyEmailWithCode(code);
      
      alertDiv.textContent = result.message;
      alertDiv.className = 'alert alert-success show';
      
      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
      
    } catch (error) {
      console.error('Verification error:', error);
      alertDiv.textContent = error.message || 'Verification failed. Please try again.';
      alertDiv.className = 'alert alert-danger show';
      
      verifyBtn.disabled = false;
      loadingDiv.style.display = 'none';
    }
  });

  // Resend verification email
  resendBtn.addEventListener('click', async () => {
    try {
      resendBtn.disabled = true;
      
      const result = await sendVerificationEmail();
      
      alertDiv.textContent = result.message;
      alertDiv.className = 'alert alert-success show';
      
      // Start cooldown timer
      let seconds = 60;
      const timerDiv = document.getElementById('resendTimer');
      
      const interval = setInterval(() => {
        seconds--;
        timerDiv.textContent = `Resend available in ${seconds}s`;
        
        if (seconds === 0) {
          clearInterval(interval);
          resendBtn.disabled = false;
          timerDiv.textContent = '';
        }
      }, 1000);
      
    } catch (error) {
      console.error('Resend error:', error);
      alertDiv.textContent = error.message || 'Failed to resend. Please try again.';
      alertDiv.className = 'alert alert-danger show';
      
      resendBtn.disabled = false;
    }
  });
</script>
```

---

## Testing

### Local Testing Checklist

- [ ] Firebase project created
- [ ] Email/Password authentication enabled
- [ ] Credentials added to `static/firebase.js`
- [ ] Signup works (`/signup`)
- [ ] Verification email received
- [ ] Email verification link works
- [ ] Login works (`/login`)
- [ ] Dashboard loads after login
- [ ] Logout works

### Production Testing Checklist

- [ ] App deployed to Render
- [ ] Domain added to Firebase Authorized Domains
- [ ] Environment variables set in Render
- [ ] Signup works in production
- [ ] Email verification works in production
- [ ] Login works in production
- [ ] Email links work correctly
- [ ] No CORS errors in browser console

### Troubleshooting Tests

```javascript
// Open browser console and run:

// Test 1: Check Firebase is loaded
console.log(typeof firebase !== 'undefined' ? 'Firebase loaded' : 'Firebase not loaded');

// Test 2: Check auth module
import { auth } from './static/firebase.js';
console.log(auth);

// Test 3: Check current user
import { getCurrentUser } from './static/auth.js';
const { user } = await getCurrentUser();
console.log(user);
```

---

## Troubleshooting

### "Firebase Configuration Error" in Console

**Problem:** Missing or incorrect Firebase credentials

**Solution:**
1. Check `static/firebase.js`
2. Verify all config values are from Firebase Console
3. Make sure you replaced `YOUR_API_KEY`, `YOUR_PROJECT_ID`, etc.
4. Reload the page

### Email Verification Link Not Working

**Problem:** Link leads to 404 or blank page

**Solution:**
1. Check that your domain is in Firebase Authorized Domains:
   - Go to **Authentication** > **Settings**
   - Verify your domain is listed
   - Wait 5-10 minutes if just added

2. For Render:
   - Domain should be exactly: `your-app-name.onrender.com`
   - Do NOT include `https://` in authorized domains

### "CORS Error" in Production

**Problem:** Firebase requests blocked by CORS

**Solution:**
1. Firebase handles CORS automatically
2. Make sure domain is in Authorized Domains
3. Check browser console for exact error
4. Restart Render service after adding domain

### Email Not Arriving

**Problem:** Verification email not received

**Solution:**
1. Check spam/promotions folder
2. Wait 30 seconds (Firebase has slight delay)
3. Check email address is correct
4. Try resending verification email
5. Check Firebase Quota: **Authentication** > **Usage**

### "Too many requests" Error

**Problem:** Rate limiting error after multiple attempts

**Solution:**
1. Wait 15 minutes before trying again
2. Firebase automatically throttles failed attempts
3. Check password is correct
4. Reset password if forgotten

### Email Already Registered Error

**Problem:** Can't signup with an email

**Solution:**
1. Try login instead (you may have already signed up)
2. If forgotten password:
   - Click "Forgot Password" on login
   - Reset via email link
3. To delete account:
   - Go to Firebase Console > **Authentication** > **Users**
   - Find user and click delete icon

---

## Important Notes

### Security

✅ **DO:**
- Keep Firebase API Key (it's public, used by web clients)
- Use Firebase Security Rules to protect data
- Enable email verification before critical operations
- Use HTTPS in production (Render handles this)

❌ **DON'T:**
- Store sensitive data in user profile displayName
- Use same password for Firebase and main account
- Disable email verification
- Share `.env` files

### Costs

Firebase Free Tier includes:
- ✅ Email/Password authentication: Unlimited
- ✅ Email verification: Unlimited
- ✅ Authentication dashboard: Free
- ✅ 50k sign-ups/month: Free

Beyond that, standard Firebase pricing applies (usually <$0.01 per 100 sign-ups)

### Email Customization

To customize verification email:
1. Go to **Authentication** > **Templates** in Firebase Console
2. Click **"Email verification"**
3. Click **"Edit template"**
4. Customize subject and email body
5. Save

---

## Next Steps

1. **Add Password Reset Flow**
   - Use `sendPasswordReset()` function in auth.js
   - Create forgot password page

2. **Add User Profile**
   - Store additional user data in Firestore
   - Link Firebase auth with your backend database

3. **Add Social Login**
   - Enable Google login
   - Enable GitHub login
   - Add provider links to signup page

4. **Monitor Usage**
   - Go to **Authentication** > **Usage**
   - Track sign-ups and active users
   - Set billing alerts

---

## Support

For issues:
1. Check [Firebase Documentation](https://firebase.google.com/docs/auth)
2. Review [Firebase Error Reference](https://firebase.google.com/docs/auth/troubleshoot)
3. Check browser console for detailed error messages
4. Visit [Firebase Community](https://groups.google.com/a/firebase.com/forum/#!forum/firebase-talk)

---

**Last Updated:** March 2026
**Firebase SDK:** v11.0.1 (Modular)
**Status:** Production Ready ✅
