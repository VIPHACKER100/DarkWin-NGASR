# DARKWIN Docker Deployment Guide

## Architecture

DARKWIN uses Docker Compose to orchestrate 4 services:

| Service | Image | Purpose |
|---|---|---|
| `postgres` | postgres:15 | Persistent scan data & findings storage |
| `redis` | redis:7 | Mesh node registry, task queue, Socket.IO broker |
| `darkwin-api` | (builds local) | Flask REST API + Socket.IO real-time bridge |
| `darkwin-worker` | (builds local) | Celery worker for background scan tasks |
| `darkwin-dashboard` | (builds local) | Next.js 16 frontend with 3D neural map |

## Quick Start

```bash
# Build and start all services
docker-compose up -d --build

# Verify all containers are running
docker-compose ps

# Access the services:
# Dashboard: http://localhost:3000
# API:       http://localhost:5000
```

## Service Configuration

### Environment Variables

Edit `config.yaml` and `.env` before starting:

```yaml
# config.yaml — mounted into API & Worker containers
database:
  url: "postgresql://darkwin:darkwin_pass@postgres:5432/darkwin_db"

redis:
  url: "redis://redis:6379/0"

ai:
  openai_api_key: "sk-..."
```

### PostgreSQL Defaults

| Setting | Value |
|---|---|
| Host | `postgres:5432` |
| User | `darkwin` |
| Password | `darkwin_pass` |
| Database | `darkwin_db` |

## Production Deployment

### Persistent Volumes

Docker Compose defines named volumes for `postgres` data. To back up:

```bash
docker run --rm -v darkwin_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres_backup.tar.gz -C /data .
```

### Scaling Workers

For distributed scanning, scale Celery workers:

```bash
docker-compose up -d --scale darkwin-worker=5
```

### Resource Limits

Add resource constraints to `docker-compose.yml`:

```yaml
services:
  darkwin-worker:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Common Operations

```bash
# View logs
docker-compose logs -f darkwin-api
docker-compose logs -f darkwin-worker

# Restart a single service
docker-compose restart darkwin-api

# Full cleanup (WARNING: deletes all data)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build darkwin-api
```

## Troubleshooting

| Issue | Fix |
|---|---|
| `Connection refused` on postgres | Container may need a moment; restart: `docker-compose restart postgres` |
| Worker not picking up tasks | Check `REDIS_URL` matches the `redis` container name |
| Dashboard shows blank 3D map | Ensure `darkwin-api` is running and accessible from dashboard container |
| Port conflicts | Change host ports in `docker-compose.yml` (e.g., `3000:3000` → `3001:3000`) |

## Without Docker

To run individual components manually:
- **Database**: `docker-compose up -d postgres redis`
- **API**: `python dashboards/backend/app.py`
- **Dashboard**: `cd dashboards/frontend-next && npm run dev`
- **Worker**: `celery -A core.scheduler worker --loglevel=info`
