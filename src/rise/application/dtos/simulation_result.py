from dataclasses import dataclass

from rise.domain.services.geometry_service import GeometryResult


@dataclass(slots=True)
class SimulationResult:
    engine_name: str
    expansion_ratio: float
    thrust_n: float
    specific_impulse_s: float
    geometry: GeometryResult