from pathlib import Path

import yaml

from rise.application.dtos.simulation_input import SimulationInput


def load_engine_config(path: str | Path) -> SimulationInput:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return SimulationInput(
        engine_name=data["name"],
        throat_area_m2=data["throat_area_m2"],
        exit_area_m2=data["exit_area_m2"],
        chamber_pressure_pa=data["chamber_pressure_pa"],
        ambient_pressure_pa=data["ambient_pressure_pa"],
        mass_flow_kg_s=data["mass_flow_kg_s"],
        exit_velocity_m_s=data["exit_velocity_m_s"],
        exit_pressure_pa=data["exit_pressure_pa"],
    )
