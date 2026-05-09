# 🛠️ DARKWIN-NGASR Troubleshooting Guide

This guide provides solutions for common issues encountered during the setup and operation of the DARKWIN-NGASR platform.

---

## 🚀 Quick Fix: The Doctor Utility
Before manual troubleshooting, always try the automated self-healing tool:
```bash
darkwin doctor --fix
```

---

## 📂 Common Environment Issues

### 1. `ModuleNotFoundError: No module named 'core'`
**Cause:** Running the script outside of the project root or without the virtual environment active.
**Fix:**
```bash
# Ensure you are in the project root
cd ~/Desktop/DarkWin-NGASR
# Activate the environment
source .venv/bin/activate
# Run the command
darkwin --help
```

### 2. `PermissionError: [Errno 13] Permission denied`
**Cause:** Log files or directories were created by a different user (e.g., via `sudo`).
**Fix:**
```bash
sudo chown -R $USER:$USER logs/ screenshots/
sudo chmod -R 775 logs/ screenshots/
```

### 3. `ImportError: cannot import name 'Sentinel' from 'typing_extensions'`
**Cause:** Your system Python has an outdated version of `typing_extensions` that is shadowing the one in your virtual environment.
**Fix:**
```bash
# Rebuild the virtual environment
rm -rf .venv
./setup.sh
source .venv/bin/activate
```

---

## 🌐 Connectivity & Services

### 4. `redis.exceptions.ConnectionError`
**Cause:** The Redis service is not running or the port is blocked.
**Fix:**
```bash
# Start Redis via Docker
docker-compose up -d redis
# Or check local service
sudo systemctl status redis
```

### 5. `psycopg2.OperationalError: connection to server at "localhost" failed`
**Cause:** PostgreSQL database is offline or credentials mismatch.
**Fix:**
1. Start DB: `docker-compose up -d postgres`
2. Check `config.yaml` matches `docker-compose.yml` (user: `darkwin`, password: `darkwin_pass`, db: `darkwin_db`).

### 6. `ModuleNotFoundError: No module named '_sqlite3'`
**Cause:** Python was built without SQLite support (common on custom Linux builds).
**Fix:**
```bash
sudo apt update && sudo apt install -y libsqlite3-dev
# You may need to reinstall python or use the primary Postgres DB
```

### 7. `FATAL: password authentication failed for user "darkwin"`
**Cause:** The password in `config.yaml` does not match the one in the database.
**Fix:** Update `config.yaml` to use `darkwin_pass` (default).

---

## 🎨 Dashboard & UI

### 6. Dashboard not loading at `http://localhost:3000`
**Cause:** Node.js dependencies missing or port conflict.
**Fix:**
```bash
cd dashboards/frontend
npm install
npm run dev
```

### 7. 3D Neural Map is empty
**Cause:** No scan data exists in the database or the backend API is offline.
**Fix:**
1. Run a hunt: `darkwin hunt example.com`
2. Ensure backend is up: `docker-compose up -d backend`

---

## 🕵️ Stealth & Proxying

### 8. `GhostMode` failing to rotate IPs
**Cause:** Proxy pool is empty or provided proxies are dead.
**Fix:**
1. Update your proxy list: `nano proxies.txt`
2. Run `darkwin proxy` to check health.

---

## 🆘 Still Stuck?
If none of the above works:
1. **Check Logs:** `darkwin logs --tail 100`
2. **Reset Platform:** `darkwin clean --all`
3. **Reinstall:** Delete the folder and clone fresh.

---
<div align="center">
<b>DARKWIN-NGASR | Autonomous · Distributed · Stealthy</b>
</div>
