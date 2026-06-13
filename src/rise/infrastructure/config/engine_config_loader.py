from pathlib import Path

import yaml
from pydantic import ValidationError

from rise.application.dtos.simulation_input import SimulationInput
from rise.infrastructure.config.schema import EngineConfigSchema


def load_engine_config(path: str | Path) -> SimulationInput:
    with open(path) as f:
        data = yaml.safe_load(f)

    try:
        schema = EngineConfigSchema(**data)
    except ValidationError as exc:
        # Build a human-readable summary of what went wrong
        messages = [f"  - {e['loc']}: {e['msg']}" for e in exc.errors()]
        raise ValueError(
            f"Invalid engine config ({path}):\n" + "\n".join(messages)
        ) from exc

    return SimulationInput(**schema.to_simulation_input())
