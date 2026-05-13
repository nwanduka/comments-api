from fastapi import FastAPI
from .routes import router
from .database import engine
from . import models
from prometheus_fastapi_instrumentator import Instrumentator

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Comments API")

# Register routes
app.include_router(router)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Health and readiness endpoints
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    return {"status": "ready"}