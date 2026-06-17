"""Simulation route — thin wrapper around RunSimulation use case.

Receives request, calls use case, returns result.
No business logic here.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from rise.application.dtos.simulation_input import SimulationInput
from rise.application.use_cases.run_simulation import RunSimulation
from rise.interfaces.api.schemas import SimulateRequest, result_to_dict

router = APIRouter()
_use_case = RunSimulation()


@router.post("/simulate")
def simulate(request: SimulateRequest) -> JSONResponse:
    """Run a simulation and return the full result as JSON."""
    sim_input = SimulationInput(
        engine_name=request.name,
        throat_area_m2=request.throat_area_m2,
        exit_area_m2=request.exit_area_m2,
        chamber_pressure_pa=request.chamber_pressure_pa,
        ambient_pressure_pa=request.ambient_pressure_pa,
        mass_flow_kg_s=request.mass_flow_kg_s,
        characteristic_length_m=request.characteristic_length_m,
        contraction_ratio=request.contraction_ratio,
        convergent_half_angle_deg=request.convergent_half_angle_deg,
        divergent_half_angle_deg=request.divergent_half_angle_deg,
        nozzle_length_method=request.nozzle_length_method,
        oxidizer=request.oxidizer,
        fuel=request.fuel,
        mixture_ratio=request.mixture_ratio,
        gamma=request.gamma,
        molecular_weight_kg_per_kmol=request.molecular_weight_kg_per_kmol,
        chamber_temperature_k=request.chamber_temperature_k,
        exit_velocity_m_s=request.exit_velocity_m_s,
        exit_pressure_pa=request.exit_pressure_pa,
        initial_chamber_pressure_pa=request.initial_chamber_pressure_pa,
        burn_time_s=request.burn_time_s,
        time_step_s=request.time_step_s,
        propellant_mass_kg=request.propellant_mass_kg,
        min_chamber_pressure_pa=request.min_chamber_pressure_pa,
        mass_flow_decay_model=request.mass_flow_decay_model,
    )
    try:
        result = _use_case.execute(sim_input)
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=500, content={"detail": f"Simulation error: {exc}"})
    return JSONResponse(content=result_to_dict(result))


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
