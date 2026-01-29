# API — Hosted PHP API Only

This project uses the **hosted PHP API** at **https://api.abhinavpaudel.com** only.

The local Python (Flask) API has been removed. The Qt browser app, React dashboard, and any extensions should call the hosted API. Health check: `https://api.abhinavpaudel.com/health` returns `{"status":"ok","message":"Backend API is running"}`.

See **BROWSER_SETUP.md** and **docs/PYTHON_APP_SETUP.md** for configuration.
