from fastapi import FastAPI

from app.routers import cameras, companies, locations, recorders

app = FastAPI(title="CAM Manager API", version="0.1.0", description="Hikvision device management API")
app.include_router(companies.router)
app.include_router(locations.router)
app.include_router(recorders.router)
app.include_router(cameras.router)


@app.get("/health", tags=["Health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
