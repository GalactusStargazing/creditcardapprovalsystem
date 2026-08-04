from fastapi import FastAPI

from app.api.routes import decisions

app = FastAPI(title="Credit Decision Service", version="1.0.0")

app.include_router(decisions.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "credit-decision-service"}
