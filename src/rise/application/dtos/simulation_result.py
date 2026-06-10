from dataclasses import dataclass

from rise.application.dtos.transient_simulation_result import (
    TransientSimulationResult,
)
from rise.domain.services.geometry_service import GeometryResult


@dataclass(slots=True)
class SimulationResult:
    engine_name: str
    expansion_ratio: float
    thrust_n: float
    specific_impulse_s: float
    geometry: GeometryResult
    transient: TransientSimulationResult | None = None