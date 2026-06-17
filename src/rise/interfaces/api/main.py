"""FastAPI application entry point.

Run with:
    uvicorn rise.interfaces.api.main:app --reload
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from rise.interfaces.api.routes.simulation import router

app = FastAPI(title="RISE API", version="1.0.0")
app.include_router(router)

# Static files mounted after routes so /simulate is not shadowed
# ponytail: StaticFiles is the built-in FastAPI way — no extra server needed
try:
    import pathlib

    _static = pathlib.Path(__file__).parent / "static"
    if _static.exists():
        app.mount("/", StaticFiles(directory=str(_static), html=True), name="static")
except Exception:  # noqa: BLE001
    pass  # static dir optional — API still works without it
