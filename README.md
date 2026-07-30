# CAM Manager

CAM Manager is a Hikvision-only device management application. Sprint 1 provides FastAPI and PostgreSQL foundations with management APIs for companies, locations, recorders, and cameras.

## Start

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend alembic upgrade head
```

Swagger UI: `http://localhost:8000/docs`

The web panel is available at `http://localhost` after `docker compose up --build -d`. It proxies API calls through Nginx at `/api`; Swagger remains available on port `8000`.

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

## Web panel

The React panel provides views for companies, locations, recorders and cameras. It can add the first three resource types, refresh recorder diagnostics, synchronize Hikvision channels and display camera snapshots.
