# DARKWIN Dashboard (Next.js 16)

Real-time security research dashboard with 3D neural attack surface visualization.

## Architecture

- **Framework**: Next.js 16 (App Router)
- **Visualization**: Three.js + react-force-graph-3d
- **Real-time**: Socket.IO client for live log streaming
- **Styling**: Tailwind CSS 4
- **Charts**: Recharts for analytics

## Quick Start

### Development
```bash
npm install
npm run dev
# Opens at http://localhost:3000
```

### Production (Docker)
```bash
docker-compose up -d
# Dashboard at http://localhost:3000
# API at http://localhost:5000
```

## Environment Variables

Create a `.env.local`:

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:5000` | Flask backend URL |
| `NEXT_PUBLIC_SOCKET_URL` | `http://localhost:5000` | Socket.IO server URL |

## Key Components

| Component | Path | Purpose |
|---|---|---|
| AttackSurfaceGraph | `src/components/AttackSurfaceGraph.tsx` | 3D neural map visualization |
| NewScanModal | `src/components/NewScanModal.tsx` | Scan configuration dialog |
| API Client | `src/lib/api.ts` | Backend API communication |

## Agent Architecture

The dashboard visualizes DARKWIN's 5-agent orchestration system defined in [AGENTS.md](./AGENTS.md):
- **Strategist** — AI reasoning loop decisions
- **Watchtower** — Mesh node health
- **Cartographer** — 3D attack surface mapping
- **Ghost** — Stealth engine status
- **Sentinel** — Vulnerability verification results

## Related

- [Flask Backend](../../dashboards/backend/)
- [Docker Deployment](../../docs/user/DOCKER.md)
- [Full API Reference](../../docs/dev/API.md)
