"""Parametric study route — thin wrapper around RunParametricStudy use case."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from rise.application.dtos.simulation_input import SimulationInput
from rise.application.use_cases.run_parametric_study import RunParametricStudy
from rise.interfaces.api.schemas import ParametricRequest, result_to_dict

router = APIRouter()
_use_case = RunParametricStudy()


@router.post("/parametric")
def parametric(request: ParametricRequest) -> JSONResponse:
    """Run a parametric sweep and return all results."""
    cfg = request.base_config
    base_input = SimulationInput(
        engine_name=cfg.name,
        throat_area_m2=cfg.throat_area_m2,
        exit_area_m2=cfg.exit_area_m2,
        chamber_pressure_pa=cfg.chamber_pressure_pa,
        ambient_pressure_pa=cfg.ambient_pressure_pa,
        mass_flow_kg_s=cfg.mass_flow_kg_s,
        characteristic_length_m=cfg.characteristic_length_m,
        contraction_ratio=cfg.contraction_ratio,
        convergent_half_angle_deg=cfg.convergent_half_angle_deg,
        divergent_half_angle_deg=cfg.divergent_half_angle_deg,
        nozzle_length_method=cfg.nozzle_length_method,
        oxidizer=cfg.oxidizer,
        fuel=cfg.fuel,
        mixture_ratio=cfg.mixture_ratio,
        gamma=cfg.gamma,
        molecular_weight_kg_per_kmol=cfg.molecular_weight_kg_per_kmol,
        chamber_temperature_k=cfg.chamber_temperature_k,
        exit_velocity_m_s=cfg.exit_velocity_m_s,
        exit_pressure_pa=cfg.exit_pressure_pa,
        initial_chamber_pressure_pa=cfg.initial_chamber_pressure_pa,
        burn_time_s=cfg.burn_time_s,
        time_step_s=cfg.time_step_s,
        propellant_mass_kg=cfg.propellant_mass_kg,
        min_chamber_pressure_pa=cfg.min_chamber_pressure_pa,
        mass_flow_decay_model=cfg.mass_flow_decay_model,
        combustion_efficiency=cfg.combustion_efficiency,
        nozzle_efficiency=cfg.nozzle_efficiency,
        altitude_sweep_m=cfg.altitude_sweep_m,
    )
    try:
        parametric_result = _use_case.execute(
            base_input=base_input,
            parameter=request.parameter,
            values=request.values,
        )
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=500, content={"detail": f"Parametric error: {exc}"})

    payload = {
        "parameter": parametric_result.parameter,
        "values": parametric_result.values,
        "compare": request.compare,
        "results": [result_to_dict(r) for r in parametric_result.results],
    }
    return JSONResponse(content=payload)
