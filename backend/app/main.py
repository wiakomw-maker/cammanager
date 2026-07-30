
from fastapi import FastAPI

app = FastAPI(
    title="CAM Manager",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "application": "CAM Manager",
        "version": "0.1.0",
        "status": "running"
    }
