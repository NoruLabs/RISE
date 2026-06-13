from pathlib import Path

import yaml

from rise.application.dtos.simulation_input import SimulationInput


def load_engine_config(path: str | Path) -> SimulationInput:
    with open(path) as f:
        data = yaml.safe_load(f)

    return SimulationInput(
        engine_name=data["name"],
        throat_area_m2=data["throat_area_m2"],
        exit_area_m2=data["exit_area_m2"],
        chamber_pressure_pa=data["chamber_pressure_pa"],
        ambient_pressure_pa=data["ambient_pressure_pa"],
        mass_flow_kg_s=data["mass_flow_kg_s"],
        characteristic_length_m=data["characteristic_length_m"],
        contraction_ratio=data["contraction_ratio"],
        convergent_half_angle_deg=data["convergent_half_angle_deg"],
        divergent_half_angle_deg=data["divergent_half_angle_deg"],
        nozzle_length_method=data["nozzle_length_method"],
        oxidizer=data.get("oxidizer"),
        fuel=data.get("fuel"),
        gamma=data.get("gamma"),
        molecular_weight_kg_per_kmol=data.get("molecular_weight_kg_per_kmol"),
        chamber_temperature_k=data.get("chamber_temperature_k"),
        exit_velocity_m_s=data.get("exit_velocity_m_s"),
        exit_pressure_pa=data.get("exit_pressure_pa"),
        initial_chamber_pressure_pa=data.get("initial_chamber_pressure_pa"),
        burn_time_s=data.get("burn_time_s"),
        time_step_s=data.get("time_step_s"),
        propellant_mass_kg=data.get("propellant_mass_kg"),
        min_chamber_pressure_pa=data.get("min_chamber_pressure_pa"),
        mixture_ratio=data.get("mixture_ratio"),
        mass_flow_decay_model=data.get("mass_flow_decay_model"),
    )
