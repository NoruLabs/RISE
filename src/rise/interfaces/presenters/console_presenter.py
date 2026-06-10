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

        if result.transient:
            t0 = result.transient[0]
            t1 = result.transient[-1]
            lines.extend(
                [
                    "",
                    "Transient (0D chamber pressure):",
                    f"  Initial chamber pressure: {t0.chamber_pressure_pa:.3f} Pa",
                    f"  Final chamber pressure:   {t1.chamber_pressure_pa:.3f} Pa",
                    f"  Initial thrust:           {t0.thrust_n:.3f} N",
                    f"  Final thrust:             {t1.thrust_n:.3f} N",
                    f"  Initial Isp:              {t0.specific_impulse_s:.3f} s",
                    f"  Final Isp:                {t1.specific_impulse_s:.3f} s",
                ]
            )

        return "\n".join(lines)
