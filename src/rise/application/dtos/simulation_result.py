from dataclasses import dataclass

from rise.domain.services.geometry_service import GeometryResult
from rise.domain.services.transient_service import TransientState


@dataclass(slots=True)
class SimulationResult:
    engine_name: str
    expansion_ratio: float
    thrust_n: float
    specific_impulse_s: float
    geometry: GeometryResult
    transient: list[TransientState] | None = None