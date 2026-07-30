# CAM Manager

CAM Manager is a Hikvision-only device management application. Sprint 1 provides FastAPI and PostgreSQL foundations with management APIs for companies, locations, recorders, and cameras.

## Start

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend alembic upgrade head
```

Swagger UI: `http://localhost:8000/docs`

## API

- `GET`, `POST` `/companies`
- `GET`, `POST` `/locations`
- `GET`, `POST` `/recorders`
- `GET`, `POST` `/cameras`

## Hikvision ISAPI

Sprint 2 adds Hikvision-only recorder actions:

- `POST /recorders/{recorder_id}/refresh` retrieves device details, online status, HDD data and temperature when supported by the recorder.
- `POST /recorders/{recorder_id}/sync` imports or updates channels discovered through ISAPI.
- `GET /recorders/{recorder_id}/cameras/{camera_id}/snapshot` proxies a current JPEG snapshot.

Most Hikvision devices use Digest Authentication. Self-signed certificates are accepted by default for appliance compatibility; set `HIKVISION_VERIFY_TLS=true` after installing a trusted certificate.
