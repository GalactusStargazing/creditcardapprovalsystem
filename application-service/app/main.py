from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import applications

app = FastAPI(title="Application Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "application-service"}
