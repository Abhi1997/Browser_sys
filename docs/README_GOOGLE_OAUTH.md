# 📧 Gmail OAuth Authentication Setup

Enable Gmail login for your Secure Academic Browser application.

## ⚡ Quick Start

### 1. Get Credentials from Google

1. Visit: **https://console.cloud.google.com/**
2. Create project → Enable APIs → Create OAuth credentials
3. Add redirect URI: `http://localhost:8080/callback`
4. Copy **Client ID** and **Client Secret**

### 2. Configure Application

**Option A: Create `.env` file (Recommended)**

```env
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

**Option B: Set environment variables**

```powershell
$env:GOOGLE_CLIENT_ID="your_client_id_here"
$env:GOOGLE_CLIENT_SECRET="your_client_secret_here"
```

### 3. Run Application

```powershell
python main.py
```

The **"Sign in with Gmail"** button will now work! 🎉

## 📚 Documentation

- **[GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md)** - Complete detailed guide
- **[SETUP_GOOGLE_OAUTH.md](SETUP_GOOGLE_OAUTH.md)** - Quick reference

## ⚠️ Current Status

If you see this warning:
```
Warning: GOOGLE_CLIENT_ID not set. Gmail OAuth will not work.
```

**Solution:** Follow the steps above to configure Google OAuth credentials.

## ✅ After Setup

- ✅ No warning message
- ✅ Gmail login button is clickable
- ✅ Can authenticate with Google account
- ✅ Users can sign in with Gmail

---

**Note:** Gmail OAuth is **optional**. You can still use username/password login without it.

