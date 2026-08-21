import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import decisions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True
)

app = FastAPI(title="Credit Decision Service", version="1.0.0")

# Disable Prometheus instrumentation during tests.
# It currently conflicts with the router structure used by this service.
if os.getenv("TESTING") != "true":
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decisions.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "credit-decision-service"}
