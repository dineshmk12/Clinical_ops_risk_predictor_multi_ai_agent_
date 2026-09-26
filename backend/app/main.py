from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routers import approvals, audit, compliance, copilot, enrollment, metrics, milestones, rca, recommendations, reports, sites, studies
from app.guardrails import GuardrailViolation
from app.hooks.rag_grounding_check import GroundingError
from app.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="Clinical Trial Health & Risk Prediction Platform",
    description="Multi-agent Clinical Operations Copilot — local prototype per CLAUDE.md",
    version="1.0.0",
)

for router in (studies, enrollment, sites, milestones, compliance, rca, recommendations, copilot, reports, audit, approvals, metrics):
    app.include_router(router.router)


@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(GuardrailViolation)
def guardrail_handler(request: Request, exc: GuardrailViolation):
    return JSONResponse(status_code=403, content={"error": str(exc)})


@app.exception_handler(GroundingError)
def grounding_handler(request: Request, exc: GroundingError):
    return JSONResponse(status_code=422, content={"error": str(exc)})


STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}
