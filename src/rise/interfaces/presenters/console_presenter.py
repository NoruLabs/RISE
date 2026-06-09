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
            f"  Throat diameter: {g.throat_diameter_m:.6f} m",
            f"  Throat radius: {g.throat_radius_m:.6f} m",
            f"  Exit diameter: {g.exit_diameter_m:.6f} m",
            f"  Chamber diameter: {g.chamber_diameter_m:.6f} m",
            f"  Chamber volume: {g.chamber_volume_m3:.6f} m³",
            f"  Converging length: {g.converging_length_m:.6f} m",
            f"  Diverging length: {g.diverging_length_m:.6f} m",
        ]
        return "\n".join(lines)
