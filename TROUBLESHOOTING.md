# 🛠️ DARKWIN-NGASR Troubleshooting Guide

**Version:** 1.0.7 | **Author:** ARYAN AHIRWAR (VIPHACKER.100)

This guide covers every known issue during setup and operation of the DARKWIN-NGASR platform.

---

## ⚡ Quick Fix: The Doctor Utility

Before manual troubleshooting, always try the automated self-healing tool first:
```bash
darkwin doctor --fix
```

---

## 📂 1. Environment & Import Issues

### `ModuleNotFoundError: No module named 'core'`
**Cause:** Running outside the project root or without the virtual environment active.
```bash
cd ~/Desktop/DarkWin-NGASR
source .venv/bin/activate
darkwin --help
```

### `ImportError: cannot import name 'Sentinel' from 'typing_extensions'`
**Cause:** System Python's `typing_extensions` shadows the one in the venv.
```bash
rm -rf .venv
./setup.sh
source .venv/bin/activate
```

### `IndentationError` or `SyntaxWarning` in any core module
**Cause:** Stale `.pyc` bytecode cache.
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
darkwin --help
```

### `darkwin: command not found`
**Cause:** Package entry point not installed.
```bash
source .venv/bin/activate
pip install -e .
darkwin --help
```

---

## 🗄️ 2. Database Issues

### `RuntimeError: Database connection failed — no working fallback available`

This error means **both** PostgreSQL and SQLite failed. The platform now uses **lazy database initialization** — `darkwin` itself will start fine, but commands that need the DB (like `targets`, `history`, `hunt`) will fail until a database is available.

**Fix (recommended): Start the PostgreSQL container**
```bash
docker-compose up -d postgres
```

Then verify it's running:
```bash
docker-compose ps
```

---

### `FATAL: password authentication failed for user "darkwin"`

**Cause:** The password in `config.yaml` doesn't match what the database was initialized with.

**Fix Option 1 — Reset the password to match `config.yaml`:**
```bash
docker-compose exec postgres psql -U postgres -c "ALTER USER darkwin WITH PASSWORD 'darkwin_pass';"
```

**Fix Option 2 — Nuke the volume and restart fresh:**
```bash
docker-compose down -v          # WARNING: deletes all DB data
docker-compose up -d postgres
```

**Credential Reference:**

| Setting | Value |
|---|---|
| Host | `localhost:5432` |
| User | `darkwin` |
| Password | `darkwin_pass` |
| Database | `darkwin_db` |

These are the defaults in both `config.yaml` and `docker-compose.yml`. If you changed one, change the other to match.

---

### `psycopg2.OperationalError: Connection refused` (server is offline)
**Cause:** PostgreSQL container is not running.
```bash
docker-compose up -d postgres

# Or, for a local PostgreSQL installation:
sudo systemctl start postgresql
```

---

### `Database does not exist` error
**Cause:** Container started but the `darkwin_db` database was never created.
```bash
docker-compose exec postgres psql -U darkwin -c "CREATE DATABASE darkwin_db;"
```

---

### `ModuleNotFoundError: No module named '_sqlite3'`
**Cause:** Python was compiled without SQLite support (common on Kali with custom Python 3.13 builds).

**Fix Option 1 — Install the missing system library:**
```bash
sudo apt update && sudo apt install -y libsqlite3-dev
# You may need to reinstall Python after this for it to take effect
```

**Fix Option 2 (Recommended) — Use PostgreSQL instead:**
```bash
docker-compose up -d postgres
```
DARKWIN will automatically use PostgreSQL and skip SQLite entirely.

---

## 🔒 3. Permission Errors

### `PermissionError: [Errno 13] Permission denied on logs/darkwin.log`
**Cause:** The `logs/` directory was created by `root` (e.g. via `sudo`).
```bash
sudo chown -R $USER:$USER logs/ screenshots/
sudo chmod -R 775 logs/ screenshots/
```

---

## 🌐 4. Connectivity & Services

### `redis.exceptions.ConnectionError`
**Cause:** Redis service is not running.
```bash
docker-compose up -d redis

# Or check local service:
sudo systemctl status redis-server
sudo systemctl start redis-server
```

### `darkwin hunt` hangs or fails with OpenAI error
**Cause:** Missing or invalid OpenAI API key in `config.yaml`.
```bash
darkwin config --view     # Check current config (keys are masked)
darkwin config --edit     # Edit config.yaml
```
Set: `openai.api_key: "sk-..."`

---

## 🎨 5. Dashboard & UI

### Dashboard not loading at `http://localhost:3000`
**Cause:** Node.js deps missing or Next.js dev server is not running.
```bash
cd dashboards/frontend-next
npm install
npm run dev
```

### 3D Neural Map is empty
**Cause:** No scan data in the database, or the backend API is offline.
1. Run a hunt: `darkwin hunt example.com`
2. Ensure backend is up: `docker-compose up -d darkwin-api`

### `NEXT_PUBLIC_API_URL` connection refused
**Cause:** The Flask/SocketIO backend is not running.
```bash
docker-compose up -d darkwin-api
```

---

## 🕵️ 6. Stealth & Proxy Issues

### `GhostMode` failing to rotate IPs
**Cause:** Proxy pool is empty or all proxies are dead.
```bash
darkwin proxy           # Check current proxy pool health
nano proxies.txt        # Update with fresh proxies
```

### Scan detected / blocked by WAF
1. Enable GhostMode: ensure `stealth.enabled: true` in `config.yaml`
2. Increase jitter: `stealth.jitter_range: [3, 10]`
3. Add more proxies to rotate IPs

---

## 🧪 7. Running Tests

### To verify core functionality:
```bash
darkwin test
# Or directly:
python -m pytest tests/ -v
```

### To run a full diagnostic:
```bash
darkwin doctor
darkwin troubleshoot --check
```

---

## 🔄 8. Full Reset (Last Resort)

If nothing else works, perform a full clean reinstall:
```bash
# Stop all containers
docker-compose down -v

# Remove Python environment
rm -rf .venv __pycache__

# Reinstall
./setup.sh
source .venv/bin/activate
docker-compose up -d

# Verify
darkwin doctor
```

---

## 🆘 Still Stuck?

1. **Check Logs:** `darkwin logs --tail 100`
2. **Reset Platform Data:** `darkwin clean --all`
3. **Reinstall Fresh:** Delete the folder and clone again:
   ```bash
   git clone https://github.com/VIPHACKER100/DarkWin-NGASR.git
   cd DarkWin-NGASR && ./setup.sh
   ```
4. **Open an Issue:** [GitHub Issues](https://github.com/VIPHACKER100/DarkWin-NGASR/issues)

---

<div align="center">
<b>DARKWIN-NGASR v1.0.7 | Autonomous · Distributed · Stealthy</b><br/>
<i>Built by ARYAN AHIRWAR (VIPHACKER.100)</i>
</div>
