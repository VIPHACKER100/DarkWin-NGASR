# DARKWIN API Documentation
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

### Version: 2.0.1

The DARKWIN Dashboard Backend provides a RESTful API to manage scans and findings.

#### Authentication
All requests must include a JWT token in the `Authorization` header.
`Authorization: <token>`

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/v1/scans` | List all scans |
| POST   | `/api/v1/scans` | Initiate a new scan |
| GET    | `/api/v1/scans/{id}` | Get detailed results for a scan |
| GET    | `/api/v1/mesh` | Get status of distributed scanning nodes |
| GET    | `/api/v1/proxy` | Get status of proxy rotation pool |
| GET    | `/api/v1/graph` | Get 3D attack surface graph data |
| GET    | `/api/v1/health` | Check API and system health status |

---
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
