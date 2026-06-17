from dataclasses import dataclass, field

from rise.application.dtos.transient_simulation_result import TransientSimulationResult
from rise.domain.services.geometry_service import GeometryResult


@dataclass(slots=True, frozen=True)
class AltitudePoint:
    altitude_m: float
    ambient_pressure_pa: float
    thrust_n: float
    specific_impulse_s: float


@dataclass(slots=True, frozen=True)
class SimulationResult:
    engine_name: str
    expansion_ratio: float
    thrust_n: float
    specific_impulse_s: float
    geometry: GeometryResult
    transient: TransientSimulationResult | None = None
    nozzle_svg: str | None = None
    altitude_sweep: list[AltitudePoint] | None = None
