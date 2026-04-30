from rise.application.dtos.simulation_result import SimulationResult
from rise.domain.entities.engine import Engine


class RunSimulation:
    def execute(self, engine: Engine) -> SimulationResult:
        engine.validate()

        return SimulationResult(
            engine_name=engine.name,
            expansion_ratio=engine.nozzle.expansion_ratio,
            thrust_n=engine.compute_thrust(),
            specific_impulse_s=engine.compute_specific_impulse(),
        )