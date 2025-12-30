# 🔐 Google OAuth Setup Guide

Complete guide to set up Gmail OAuth authentication for the Secure Academic Browser.

## 📋 Prerequisites

1. Google account
2. Access to [Google Cloud Console](https://console.cloud.google.com/)

## 🚀 Step-by-Step Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `Secure Academic Browser` (or any name)
4. Click **"Create"**
5. Wait for project creation to complete

### Step 2: Enable Required APIs

1. In the Google Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for and enable:
   - **Google+ API** (or **People API**)
   - **OAuth2 API**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - **User Type**: Choose **"External"** (for testing) or **"Internal"** (for organization)
   - Click **"Create"**
   - Fill in the consent screen:
     - **App name**: `Secure Academic Browser`
     - **User support email**: Your email
     - **Developer contact information**: Your email
   - Click **"Save and Continue"**
   - **Scopes**: Click **"Save and Continue"** (add scopes if needed)
   - **Test users**: Add test users if using External type, then click **"Save and Continue"**
   - Click **"Back to Dashboard"**

4. Now create OAuth Client ID:
   - **Application type**: Select **"Web application"**
   - **Name**: `Secure Academic Browser Desktop`
   - **Authorized redirect URIs**: Add:
     ```
     http://localhost:8080/callback
     ```
   - Click **"Create"**

5. **Copy your credentials:**
   - **Client ID**: Copy this (looks like: `123456789-abcdefg.apps.googleusercontent.com`)
   - **Client Secret**: Copy this (looks like: `GOCSPX-abcdefghijklmnop`)

### Step 4: Configure Your Application

#### Option 1: Using .env File (Recommended)

Create a `.env` file in your project root (if it doesn't exist):

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=Innovation
DB_NAME=edubrowser
DB_PORT=3307

# API Configuration
API_PORT=5000
VITE_API_URL=http://localhost:5000

# Dashboard Configuration
DASHBOARD_PORT=3000
```

**Replace:**
- `your_client_id_here` with your actual Client ID
- `your_client_secret_here` with your actual Client Secret

#### Option 2: Environment Variables (Windows PowerShell)

```powershell
$env:GOOGLE_CLIENT_ID="your_client_id_here"
$env:GOOGLE_CLIENT_SECRET="your_client_secret_here"
python main.py
```

#### Option 3: Environment Variables (Windows CMD)

```cmd
set GOOGLE_CLIENT_ID=your_client_id_here
set GOOGLE_CLIENT_SECRET=your_client_secret_here
python main.py
```

#### Option 4: Environment Variables (Linux/Mac)

```bash
export GOOGLE_CLIENT_ID="your_client_id_here"
export GOOGLE_CLIENT_SECRET="your_client_secret_here"
python main.py
```

## ✅ Verification

After setting up credentials:

1. **Run the application:**
   ```powershell
   python main.py
   # Or with Docker MySQL:
   $env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
   ```

2. **Check for warning:**
   - If you see: `Warning: GOOGLE_CLIENT_ID not set` → Credentials not loaded
   - If no warning → Credentials are set correctly ✅

3. **Test Gmail login:**
   - Click **"Sign in with Gmail"** button in login window
   - Should open Google authentication page
   - After authorizing, should redirect back to application

## 🔒 Security Best Practices

1. **Never commit `.env` file to version control**
   - Add `.env` to `.gitignore`
   - Use `.env.example` as a template (without real credentials)

2. **Keep credentials secure:**
   - Don't share credentials publicly
   - Rotate credentials if compromised
   - Use different credentials for development/production

3. **OAuth Consent Screen:**
   - For production, complete the verification process
   - For testing, add test users in Google Cloud Console

## 📝 Redirect URI Configuration

The application uses this redirect URI:
```
http://localhost:8080/callback
```

Make sure this exact URI is added in:
- Google Cloud Console → OAuth 2.0 Client → Authorized redirect URIs

**Important:** The redirect URI must match exactly (including protocol, port, and path).

## 🐛 Troubleshooting

### "Invalid client" error

- ✅ Check Client ID is correct (no extra spaces)
- ✅ Check Client Secret is correct
- ✅ Verify credentials are from the correct Google Cloud project

### "Redirect URI mismatch" error

- ✅ Ensure `http://localhost:8080/callback` is added in Google Cloud Console
- ✅ Check for typos (http vs https, trailing slashes)
- ✅ Verify the exact URI matches

### "Access blocked" error

- ✅ If using External app type, add your email as a test user
- ✅ Complete OAuth consent screen configuration
- ✅ For production, verify your app in Google Cloud Console

### Warning still appears after setting credentials

- ✅ Check `.env` file is in project root directory
- ✅ Verify environment variables are set correctly
- ✅ Restart the application after setting variables
- ✅ Check for typos in variable names: `GOOGLE_CLIENT_ID` (not `GOOGLE_CLIENT_ID_`)

### Gmail button doesn't work

- ✅ Check credentials are set correctly
- ✅ Verify `requests` library is installed: `pip install requests`
- ✅ Check internet connection
- ✅ Verify Google APIs are enabled in Cloud Console

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

## 🎯 Quick Reference

**Required Environment Variables:**
```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

**Redirect URI:**
```
http://localhost:8080/callback
```

**Required Scopes:**
- `openid`
- `email`
- `profile`

---

**That's it!** Once configured, users can sign in with their Gmail accounts. 🎉

