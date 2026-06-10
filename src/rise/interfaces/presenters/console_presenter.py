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
            t = result.transient
            avg_thrust = sum(t.thrust_n) / len(t.thrust_n) if t.thrust_n else 0.0
            peak_pressure = max(t.chamber_pressure_pa) if t.chamber_pressure_pa else 0.0
            burn_time = t.time_s[-1] - t.time_s[0] if len(t.time_s) > 1 else 0.0
            lines.extend(
                [
                    "",
                    "Transient (0D chamber pressure):",
                    f"  Initial pressure: {t.chamber_pressure_pa[0]:.3f} Pa",
                    f"  Peak pressure:    {peak_pressure:.3f} Pa",
                    f"  Final pressure:   {t.chamber_pressure_pa[-1]:.3f} Pa",
                    f"  Average thrust:   {avg_thrust:.3f} N",
                    f"  Burn time:        {burn_time:.3f} s",
                ]
            )
            if t.remaining_propellant_kg:
                if t.remaining_propellant_kg[-1] <= 0:
                    lines.append(
                        f"  Burn complete at: {t.time_s[-1]:.3f} s"
                    )
                else:
                    lines.append(
                        f"  Remaining propellant: {t.remaining_propellant_kg[-1]:.3f} kg"
                    )

        return "\n".join(lines)
