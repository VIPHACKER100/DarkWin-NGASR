# DARKWIN Dashboard Guide

The DARKWIN dashboard is a real-time web interface for monitoring autonomous security research operations, visualizing attack surfaces, and managing scan results.

## Setup

### Option A: Docker (Recommended)

```bash
docker-compose up -d --build
# Dashboard: http://localhost:3000
# API:       http://localhost:5000
```

### Option B: Manual Development

**1. Start the backend:**
```bash
# Ensure PostgreSQL and Redis are running
docker-compose up -d postgres redis

# Start Flask API + SocketIO
python dashboards/backend/app.py
# API runs on http://localhost:5000
```

**2. Start the frontend:**
```bash
cd dashboards/frontend-next
npm install
npm run dev
# Dashboard runs on http://localhost:3000
```

## Features

### 3D Neural Attack Surface Map
Rendered using Three.js via `react-force-graph-3d`. Nodes represent targets, subdomains, and findings. Edges represent relationships discovered during scanning.

- **Pan**: Click + drag
- **Zoom**: Scroll
- **Rotate**: Right-click + drag
- **Inspect**: Click a node for details

### Live Log Stream
Real-time Socket.IO connection streams scan events from the AI reasoning loop, module execution, and vulnerability verification directly to the browser.

### Report Center
Once a scan completes, navigate to Reports to generate AI-synthesized PDF, HTML, or Markdown reports.

### Scan Management
Use the "New Scan" modal to configure and launch hunts directly from the dashboard.

## Environment Variables

Create `dashboards/frontend-next/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_SOCKET_URL=http://localhost:5000
```

## Troubleshooting

| Issue | Fix |
|---|---|
| Dashboard loads but no data | Ensure a scan has run: `darkwin hunt example.com` |
| 3D map is empty | Backend API may be offline; check `docker-compose ps` |
| `CORS` errors in browser console | Ensure Flask backend has CORS enabled (v2.0.2+) |
| Socket.IO not connecting | Verify Redis is running and `REDIS_URL` is correct |
| `npm run dev` fails | Run `node --version` — requires Node.js 20+ |

## Agent Status Panel

The dashboard reflects the status of DARKWIN's 5 agentic subsystems:

| Agent | What it shows |
|---|---|
| Strategist | Current AI decision and reasoning trace |
| Watchtower | Connected mesh nodes and their health |
| Cartographer | The 3D neural map itself |
| Ghost | Stealth mode status, proxy count, jitter settings |
| Sentinel | Verified vs unverified findings counter |
