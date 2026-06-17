"""FastAPI application entry point.

Run with:
    uvicorn rise.interfaces.api.main:app --reload
"""
import pathlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from rise.interfaces.api.routes.parametric import router as parametric_router
from rise.interfaces.api.routes.simulation import router as simulation_router

app = FastAPI(title="RISE API", version="1.2.0")
app.include_router(simulation_router)
app.include_router(parametric_router)

_static = pathlib.Path(__file__).parent / "static"
if _static.exists():
    app.mount("/", StaticFiles(directory=str(_static), html=True), name="static")
