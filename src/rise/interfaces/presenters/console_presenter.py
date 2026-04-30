from rise.application.dtos.simulation_result import SimulationResult


class ConsolePresenter:
    def present(self, result: SimulationResult) -> None:
        print("RISE - Rocket Integrated Simulation Environment")
        print(f"Engine: {result.engine_name}")
        print(f"Expansion ratio: {result.expansion_ratio:.3f}")
        print(f"Thrust: {result.thrust_n:.3f} N")
        print(f"Specific impulse: {result.specific_impulse_s:.3f} s")
