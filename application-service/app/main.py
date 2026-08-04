from fastapi import FastAPI

from app.api.routes import applications

app = FastAPI(title="Application Service", version="1.0.0")

app.include_router(applications.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "application-service"}
