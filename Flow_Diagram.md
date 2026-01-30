# Authentication System - Visual Flow Diagrams

## 1. User Registration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER REGISTRATION FLOW                      │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ▼
[User visits /signup]
  │
  ▼
[Fills signup form]
  │  (Name, Email, Password, Confirm Password)
  ▼
[Client-side validation]
  │  • Non-empty fields
  │  • Password length ≥ 6
  │  • Passwords match
  ▼
[Submit to /api/signup]
  │
  ▼
[Server-side validation]
  │  • Email format valid
  │  • Email not already registered
  │  • Password requirements met
  ▼
[Create user account]
  │  • Hash password with bcrypt
  │  • Store in database
  │  • Generate user ID
  ▼
[Generate verification code]
  │  • Random 6-digit code
  │  • Set expiration (10 min)
  │  • Store in database
  ▼
[Send verification email]
  │  • Via SMTP or mock mode
  │  • Include verification code
  │  • HTML formatted
  ▼
[Redirect to /verify-email]
  │
  ▼
REGISTRATION COMPLETE
```

## 2. Email Verification Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   EMAIL VERIFICATION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

START (from registration)
  │
  ▼
[User visits /verify-email]
  │
  ▼
[Display verification form]
  │  • Show email address
  │  • Verification code input
  │  • Resend code button
  ▼
[User enters code]
  │
  ▼
[Submit to /api/verify-email]
  │
  ▼
[Validate code]
  │  • Code exists in database
  │  • Code not expired
  │  • Code not already used
  ▼
  ├─ CODE VALID
  │   ▼
  │  [Mark code as used]
  │   │
  │   ▼
  │  [Mark email as verified]
  │   │
  │   ▼
  │  [Send welcome email]
  │   │
  │   ▼
  │  [Redirect to /login]
  │   │
  │   ▼
  │  ✅ VERIFICATION SUCCESS
  │
  └─ CODE INVALID/EXPIRED
      ▼
     [Show error message]
      │
      ▼
     [User can resend code]
      │
      ▼
     [Try again or signup again]
```

## 3. Resend Code Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      RESEND CODE FLOW                            │
└─────────────────────────────────────────────────────────────────┘

START (from /verify-email page)
  │
  ▼
[User clicks "Resend Code"]
  │
  ▼
[Send request to /api/resend-code]
  │
  ▼
[Validate user exists]
  │  • Email in database
  │  • Email not verified yet
  ▼
[Generate new code]
  │  • Random 6-digit code
  │  • New 10-minute expiration
  ▼
[Store new code]
  │  • Update database
  │  • Old code invalidated by time
  ▼
[Send email with new code]
  │
  ▼
[Show success message]
  │
  ▼
[Start 60-second cooldown]
  │  • Disable resend button
  │  • Show countdown timer
  ▼
✅ CODE RESENT
```

## 4. Login Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        LOGIN FLOW                                │
└─────────────────────────────────────────────────────────────────┘

START (from /verify-email or direct)
  │
  ▼
[User visits /login]
  │
  ▼
[Fills login form]
  │  (Email, Password, Remember Me)
  ▼
[Submit to /login endpoint]
  │
  ▼
[Validate credentials]
  │  • Email format valid
  │  • Email exists in database
  │  • Email is verified
  │  • Password matches hash
  ▼
  ├─ EMAIL NOT VERIFIED
  │   ▼
  │  [Show error]
  │   │
  │   ▼
  │  [Offer to go to verification page]
  │   │
  │   ▼
  │  ❌ LOGIN BLOCKED
  │
  ├─ INVALID EMAIL
  │   ▼
  │  [Show: "Invalid email or password"]
  │   │
  │   ▼
  │  ❌ LOGIN FAILED
  │
  ├─ INVALID PASSWORD
  │   ▼
  │  [Show: "Invalid email or password"]
  │   │
  │   ▼
  │  ❌ LOGIN FAILED
  │
  └─ ALL VALID
      ▼
     [Generate JWT token]
      │
      ▼
     [Create session]
      │  • Set session_id
      │  • Store email
      │  • Store name
      │  • Set logged_in flag
      ▼
     [If "Remember Me" checked]
      │  • Save email in localStorage
      ▼
     [Redirect to /dashboard]
      │
      ▼
     ✅ LOGIN SUCCESS
```

## 5. Database Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                   DATABASE SCHEMA                             │
└──────────────────────────────────────────────────────────────┘

users TABLE
├─ id (INTEGER, PRIMARY KEY)
├─ email (TEXT, UNIQUE) ◄───────────┐
├─ name (TEXT)                       │
├─ password_hash (TEXT)              │ FOREIGN KEY
├─ is_verified (INTEGER)             │
├─ created_at (TIMESTAMP)            │
└─ updated_at (TIMESTAMP)            │
                                     │
email_verification TABLE             │
├─ id (INTEGER, PRIMARY KEY)         │
├─ email (TEXT) ────────────────────┘ (FOREIGN KEY)
├─ verification_code (TEXT)
├─ created_at (TIMESTAMP)
├─ expires_at (TIMESTAMP)
└─ is_used (INTEGER)

RELATIONSHIP:
One user can have multiple verification codes
(but only active ones before expiration)
```

## 6. Session Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│                   SESSION LIFECYCLE                           │
└──────────────────────────────────────────────────────────────┘

[User Logs In]
        │
        ▼
[Session Created]
    ├─ session_id: random hex
    ├─ user_id: database user ID
    ├─ email: user email
    ├─ name: user name
    ├─ logged_in: true
    └─ created_at: timestamp
        │
        ▼
[User Browses Application]
    │  Every request includes session
    │  ├─ Check logged_in flag
    │  ├─ Verify session exists
    │  └─ Allow access to protected routes
        │
        ▼
[Sessions Persist]
    │  ├─ Across page reloads
    │  ├─ Across browser tabs
    │  ├─ In localStorage (JWT token)
    │  └─ For 7 days (configurable)
        │
        ▼
[User Logs Out]
    │
    ▼
[Session Destroyed]
    ├─ Clear all session data
    ├─ Clear localStorage
    ├─ Clear JWT token
    └─ Redirect to /login
        │
        ▼
[Session Ended]
```

## 7. Password Security Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  PASSWORD SECURITY FLOW                       │
└──────────────────────────────────────────────────────────────┘

SIGNUP:
[User enters password]
        │
        ▼
[Client validates]
    └─ Length ≥ 6
        │
        ▼
[Password sent to server]
        │
        ▼
[Server validates again]
        │
        ▼
[Generate bcrypt salt]
        │
        ▼
[Hash password with salt]
    └─ Cost factor: 10-12
        │
        ▼
[Store HASH (not password)]
        │
        ▼
✅ PASSWORD SECURE

LOGIN:
[User enters password]
        │
        ▼
[Fetch stored hash from DB]
        │
        ▼
[Compare password with hash]
    └─ Using bcrypt.checkpw()
        │
        ├─ MATCH ──────► ✅ VERIFIED
        │
        └─ NO MATCH ───► ❌ REJECTED
```

## 8. Error Handling Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   ERROR HANDLING FLOW                         │
└──────────────────────────────────────────────────────────────┘

[User Action]
    │
    ▼
[Error Occurs]
    │
    ├─ Validation Error
    │   ├─ Invalid email format
    │   ├─ Password too short
    │   ├─ Fields empty
    │   │
    │   ▼
    │  [Show specific error]
    │   └─ "Email is invalid"
    │   └─ "Password must be 6+ characters"
    │   └─ "All fields required"
    │
    ├─ Database Error
    │   ├─ Email already exists
    │   ├─ User not found
    │   │
    │   ▼
    │  [Show user-friendly error]
    │   └─ "Email already registered"
    │   └─ "User not found"
    │
    ├─ Code Error
    │   ├─ Code not found
    │   ├─ Code expired
    │   ├─ Code already used
    │   │
    │   ▼
    │  [Show clear message]
    │   └─ "Invalid verification code"
    │   └─ "Code expired - request new one"
    │
    └─ System Error
        ├─ Email sending failed
        ├─ Database unavailable
        │
        ▼
       [Log error, show generic message]
        └─ "An error occurred. Try again."

[Continue/Retry/Exit]
```

## 9. Complete User Journey

```
┌────────────────────────────────────────────────────────────────┐
│                   COMPLETE USER JOURNEY                         │
└────────────────────────────────────────────────────────────────┘

NEW USER:
┌──────┐
│START │
└──┬───┘
   │
   ▼
[Visit /signup] ──────────► [Fill Form]
   │                              │
   │◄─────────────────────────────┘
   ▼
[Validate & Create Account]
   │
   ▼
[Generate Verification Code]
   │
   ▼
[Send Email]
   │
   ▼
[Redirect to /verify-email] ──► [Enter Code]
   │                              │
   │◄─────────────────────────────┘
   ▼
[Validate Code]
   │
   ▼
[Mark Email Verified]
   │
   ▼
[Redirect to /login] ──────► [Enter Credentials]
   │                              │
   │◄─────────────────────────────┘
   ▼
[Verify Password]
   │
   ▼
[Create Session]
   │
   ▼
[Redirect to /dashboard]
   │
   ▼
✅ LOGGED IN

RETURNING USER:
[Visit /login] ───► [Enter Credentials]
   │                      │
   │◄─────────────────────┘
   ▼
[Verify Email & Password]
   │
   ▼
[Create Session]
   │
   ▼
[Redirect to /dashboard]
   │
   ▼
✅ LOGGED IN

LOGOUT:
[Click Logout] ───► [Clear Session]
   │                      │
   │◄─────────────────────┘
   ▼
[Redirect to /login]
   │
   ▼
✅ LOGGED OUT
```

## 10. Component Interaction Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                COMPONENT INTERACTION DIAGRAM                    │
└────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Frontend      │
│  (HTML/JS)      │
│ ┌─────────────┐ │
│ │ signup.html │ │
│ ├─────────────┤ │
│ │ login.html  │ │
│ ├─────────────┤ │
│ │verify_email │ │
│ └─────────────┘ │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   Backend       │
│  (Flask)        │
│ ┌─────────────┐ │
│ │ web_agent   │ │ (Routes)
│ ├─────────────┤ │
│ │email_service│ │ (Emails)
│ ├─────────────┤ │
│ │ database.py │ │ (Data)
│ └─────────────┘ │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   (SQLite)      │
│ ┌─────────────┐ │
│ │   users     │ │
│ ├─────────────┤ │
│ │email_verify │ │
│ └─────────────┘ │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SMTP Server    │
│   (Gmail/etc)   │
└─────────────────┘
```

---

**These diagrams show the complete flow of the authentication system from user registration through login and beyond.**
