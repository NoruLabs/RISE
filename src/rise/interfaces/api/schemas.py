"""Request and response Pydantic models for the RISE API.

All I/O validation happens here — FastAPI enforces these automatically.
Domain logic stays in the domain layer; these are wire formats only.
"""
from dataclasses import asdict

from pydantic import BaseModel, Field

from rise.application.dtos.simulation_result import SimulationResult


class SimulateRequest(BaseModel):
    """Engine config sent as JSON to POST /simulate.

    Mirrors EngineConfigSchema but lives in the interfaces layer
    so the API contract is independent of the config-file schema.
    """

    name: str
    throat_area_m2: float = Field(gt=0)
    exit_area_m2: float = Field(gt=0)
    chamber_pressure_pa: float = Field(gt=0)
    ambient_pressure_pa: float = Field(ge=0)
    mass_flow_kg_s: float = Field(gt=0)
    characteristic_length_m: float = Field(gt=0)
    contraction_ratio: float = Field(gt=0)
    convergent_half_angle_deg: float = Field(gt=0)
    divergent_half_angle_deg: float = Field(gt=0)
    nozzle_length_method: str
    oxidizer: str | None = None
    fuel: str | None = None
    mixture_ratio: float | None = Field(default=None, gt=0)
    gamma: float | None = Field(default=None, gt=0)
    molecular_weight_kg_per_kmol: float | None = Field(default=None, gt=0)
    chamber_temperature_k: float | None = Field(default=None, gt=0)
    exit_velocity_m_s: float | None = Field(default=None, gt=0)
    exit_pressure_pa: float | None = Field(default=None, ge=0)
    initial_chamber_pressure_pa: float | None = Field(default=None, gt=0)
    burn_time_s: float | None = Field(default=None, gt=0)
    time_step_s: float | None = Field(default=None, gt=0)
    propellant_mass_kg: float | None = Field(default=None, ge=0)
    min_chamber_pressure_pa: float | None = Field(default=None, ge=0)
    mass_flow_decay_model: str | None = None
    # Stage 20 fields (default 1.0 — no breaking change)
    combustion_efficiency: float = Field(default=1.0, gt=0, le=1.0)
    nozzle_efficiency: float = Field(default=1.0, gt=0, le=1.0)
    # Stage 20 field
    altitude_sweep_m: list[float] | None = None


def result_to_dict(result: SimulationResult) -> dict:  # type: ignore[type-arg]
    """Convert frozen dataclass result to a JSON-serialisable dict.

    ponytail: dataclasses.asdict does a full recursive copy — fine for our sizes.
    """
    return asdict(result)  # type: ignore[call-overload]
