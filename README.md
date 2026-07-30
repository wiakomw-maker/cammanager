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
