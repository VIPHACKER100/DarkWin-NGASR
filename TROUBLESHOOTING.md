# DARKWIN Troubleshooting Guide
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

### Common Issues

#### 1. Database Connection Failed
- Ensure PostgreSQL is running: `docker-compose ps`
- Check `config.yaml` database URL.

#### 2. Celery Worker Not Receiving Tasks
- Ensure Redis is running.
- Restart worker: `celery -A core.scheduler worker --loglevel=info`

#### 3. Tool Not Found (nmap, ffuf, etc.)
- Run `bash setup.sh` to check for missing binaries.
- Ensure binaries are in your PATH or configured in `config.yaml`.

---
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
