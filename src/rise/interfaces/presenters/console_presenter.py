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
            lines.extend(
                [
                    "",
                    "Transient (0D chamber pressure):",
                    f"  Initial chamber pressure: {t.chamber_pressure_pa[0]:.3f} Pa",
                    f"  Final chamber pressure:   {t.chamber_pressure_pa[-1]:.3f} Pa",
                    f"  Initial thrust:           {t.thrust_n[0]:.3f} N",
                    f"  Final thrust:             {t.thrust_n[-1]:.3f} N",
                    f"  Initial Isp:              {t.specific_impulse_s[0]:.3f} s",
                    f"  Final Isp:                {t.specific_impulse_s[-1]:.3f} s",
                ]
            )
            if t.remaining_propellant_kg:
                if t.remaining_propellant_kg[-1] <= 0:
                    lines.append(
                        f"  Burn complete at:         {t.time_s[-1]:.3f} s"
                    )
                else:
                    lines.append(
                        f"  Remaining propellant:      {t.remaining_propellant_kg[-1]:.3f} kg"
                    )

        return "\n".join(lines)
