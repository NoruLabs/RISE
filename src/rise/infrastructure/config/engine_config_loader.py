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
        oxidizer=data["oxidizer"],
        fuel=data["fuel"],
        gamma=data["gamma"],
        molecular_weight_kg_per_kmol=data["molecular_weight_kg_per_kmol"],
        chamber_temperature_k=data["chamber_temperature_k"],
        characteristic_length_m=data["characteristic_length_m"],
        contraction_ratio=data["contraction_ratio"],
        convergent_half_angle_deg=data["convergent_half_angle_deg"],
        divergent_half_angle_deg=data["divergent_half_angle_deg"],
        nozzle_length_method=data["nozzle_length_method"],
    )
