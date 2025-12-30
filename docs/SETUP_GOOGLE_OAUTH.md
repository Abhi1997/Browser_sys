# ⚡ Quick Setup: Google OAuth

Quick guide to enable Gmail login.

## 🚀 5-Minute Setup

### 1. Get Google OAuth Credentials

1. Go to: https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Go to **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
5. Configure consent screen (if first time)
6. Create OAuth client:
   - Type: **Web application**
   - Name: `Secure Academic Browser`
   - Redirect URI: `http://localhost:8080/callback`
7. **Copy Client ID and Client Secret**

### 2. Add to .env File

Create `.env` file in project root:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

### 3. Done! ✅

Run your application:
```powershell
python main.py
```

The Gmail login button will now work!

---

**Detailed instructions:** See [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md)

