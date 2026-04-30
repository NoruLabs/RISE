from dataclasses import dataclass


@dataclass(slots=True)
class SimulationResult:
    engine_name: str
    expansion_ratio: float
    thrust_n: float
    specific_impulse_s: float