"""RunParametricStudy — sweeps one parameter over N values.

Does not know about YAML or HTTP.
Receives a base SimulationInput and a sweep spec; delegates each run
to RunSimulation.  One responsibility: orchestrate the loop.
"""
from __future__ import annotations

import dataclasses

from rise.application.dtos.parametric_result import ParametricResult
from rise.application.dtos.simulation_input import SimulationInput
from rise.application.use_cases.run_simulation import RunSimulation

_MAX_VALUES = 50


class RunParametricStudy:
    def __init__(self) -> None:
        self._sim = RunSimulation()

    def execute(
        self,
        base_input: SimulationInput,
        parameter: str,
        values: list[float],
    ) -> ParametricResult:
        """Run the simulation once per value, collecting all results.

        Args:
            base_input:  The base engine config — immutable.
            parameter:   A field name on SimulationInput (e.g. 'mixture_ratio').
            values:      List of float values to sweep.  Capped at 50.

        Returns:
            ParametricResult with one SimulationResult per value.

        Raises:
            ValueError: if parameter is not a valid field or too many values.
        """
        if len(values) > _MAX_VALUES:
            raise ValueError(
                f"Sweep exceeds {_MAX_VALUES} values (got {len(values)}). "
                "Reduce the number of sweep points."
            )

        valid_fields = {f.name for f in dataclasses.fields(SimulationInput)}
        if parameter not in valid_fields:
            raise ValueError(
                f"'{parameter}' is not a valid SimulationInput field. "
                f"Valid fields: {sorted(valid_fields)}"
            )

        results = []
        for v in values:
            # dataclasses.replace creates a new frozen copy with one field changed
            modified = dataclasses.replace(base_input, **{parameter: v})
            results.append(self._sim.execute(modified))

        return ParametricResult(
            parameter=parameter,
            values=list(values),
            results=results,
        )
