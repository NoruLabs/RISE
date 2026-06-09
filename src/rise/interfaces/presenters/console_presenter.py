from rise.application.dtos.simulation_result import SimulationResult


class ConsolePresenter:
    def present(self, result: SimulationResult) -> str:
        g = result.geometry
        lines = [
            "RISE - Rocket Integrated Simulation Environment",
            f"Engine: {result.engine_name}",
            f"Expansion ratio: {result.expansion_ratio:.3f}",
            f"Thrust: {result.thrust_n:.3f} N",
            f"Specific impulse: {result.specific_impulse_s:.3f} s",
            "",
            "Geometry:",
            f"  Throat diameter:    {g.throat_diameter_m:.6f} m",
            f"  Chamber diameter:   {g.chamber_diameter_m:.6f} m",
            f"  Chamber length:     {g.chamber_length_m:.6f} m",
            f"  Nozzle exit diameter: {g.exit_diameter_m:.6f} m",
            f"  Expansion ratio:    {g.expansion_ratio:.3f}",
        ]
        return "\n".join(lines)
