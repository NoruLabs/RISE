"""ParametricResult DTO — holds all SimulationResult objects from a sweep."""
from dataclasses import dataclass

from rise.application.dtos.simulation_result import SimulationResult


@dataclass(slots=True, frozen=True)
class ParametricResult:
    parameter: str
    values: list[float]
    results: list[SimulationResult]
