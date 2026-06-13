# RISE

[![CI](https://github.com/NoruLabs/RISE/actions/workflows/ci.yml/badge.svg)](https://github.com/NoruLabs/RISE/actions/workflows/ci.yml)

RISE is the **Rocket Integrated Simulation Environment**. It is a Python package for modeling rocket engine operating points and computing performance values such as expansion ratio, thrust, specific impulse, and 0D chamber-pressure transients.

The engine uses a **layered architecture** (domain / application / infrastructure / interfaces) and integrates with [RocketCEA](https://rocketcea.readthedocs.io) for thermochemistry. You can run it with propellant names (LOX, LH2, etc.) and let CEA compute gamma, molecular weight, and temperature, or you can provide those values manually.

---

## Install

Create a virtual environment, then install the package with its development tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Requires Python 3.11 or newer.

---

## Run a Simulation

Run the CLI with an engine config file:

```powershell
rise --config configs/engines/pressure_fed_test.yaml
```

Expected output:

```text
RISE - Rocket Integrated Simulation Environment
Engine: pressure-fed-test
Expansion ratio: 6.000
Thrust: 6937.820 N
Specific impulse: 393.034 s

Geometry:
  Throat diameter:    0.031915 m
  Chamber diameter:   0.071365 m
  Chamber length:     0.152400 m
  Nozzle exit diameter: 0.078176 m
  Expansion ratio:    6.000

Transient (0D chamber pressure):
  Initial pressure: 2000000.000 Pa
  Peak pressure:    5436476.555 Pa
  Final pressure:   5436476.555 Pa
  Average thrust:   6831.642 N
  Burn time:        10.000 s
  Remaining propellant: 0.000 kg

Plots saved to: output
```

### CLI Options

| Flag | Description |
|------|-------------|
| `--config` | **Required.** Path to the engine YAML config file. |
| `--output-dir` | Directory for plot output (default: `output`). |
| `--no-plots` | Skip plot generation. |

Example without plots:

```powershell
rise --config configs/engines/pressure_fed_test.yaml --no-plots
```

---

## Engine Configuration

Engine configs live in `configs/engines/` as YAML files. RISE validates every field with Pydantic and gives a clear error if a value is missing, has the wrong type, or violates a constraint (e.g. negative pressure).

### Required Fields

| Field | Type | Description | Units |
|-------|------|-------------|-------|
| `name` | string | Engine identifier | — |
| `throat_area_m2` | float | Throat area | m² (must be > 0) |
| `exit_area_m2` | float | Exit area | m² (must be >= throat_area_m2) |
| `chamber_pressure_pa` | float | Chamber pressure | Pa (must be > 0) |
| `ambient_pressure_pa` | float | Ambient pressure | Pa (must be >= 0) |
| `mass_flow_kg_s` | float | Mass flow rate | kg/s (must be > 0) |
| `characteristic_length_m` | float | Characteristic length L* | m (must be > 0) |
| `contraction_ratio` | float | Chamber-to-throat area ratio | — (must be > 0) |
| `convergent_half_angle_deg` | float | Convergent half-angle | degrees (must be > 0) |
| `divergent_half_angle_deg` | float | Divergent half-angle | degrees (must be > 0) |
| `nozzle_length_method` | string | Length calculation method | e.g. `80_percent_bell` |

### Optional Propellant / Chemistry Fields

| Field | Type | Description |
|-------|------|-------------|
| `oxidizer` | string | Oxidizer propellant name (e.g. `LOX`) |
| `fuel` | string | Fuel propellant name (e.g. `LH2`) |
| `mixture_ratio` | float | O/F mixture ratio (must be > 0) |
| `gamma` | float | Ratio of specific heats (must be > 0) |
| `molecular_weight_kg_per_kmol` | float | Molecular weight (must be > 0) |
| `chamber_temperature_k` | float | Chamber temperature (must be > 0) |
| `exit_velocity_m_s` | float | Exit velocity (must be > 0) |
| `exit_pressure_pa` | float | Exit pressure (must be >= 0) |

### Optional Transient Fields

| Field | Type | Description |
|-------|------|-------------|
| `initial_chamber_pressure_pa` | float | Initial pressure for 0D transient (must be > 0) |
| `burn_time_s` | float | Total burn time (must be > 0) |
| `time_step_s` | float | Integration time step (must be > 0) |
| `propellant_mass_kg` | float | Initial propellant mass (must be >= 0) |
| `min_chamber_pressure_pa` | float | Minimum pressure cutoff (must be >= 0) |
| `mass_flow_decay_model` | string | Mass flow decay model name |

### Adding a New Engine

1. Create a new YAML file in `configs/engines/`.
2. Fill the required fields and any optional fields you need.
3. Run it:

```powershell
rise --config configs/engines/my_engine.yaml
```

---

## Architecture

RISE uses a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│  interfaces                             │  CLI entry point, presenters
│  - cli/main.py                          │  - argparse + main() loop
│  - presenters/console_presenter.py      │  - formats SimulationResult for stdout
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  application                            │  Use cases, DTOs, validation
│  - use_cases/run_simulation.py          │  - orchestrates the simulation pipeline
│  - dtos/simulation_input.py             │  - input/output data objects
│  - dtos/simulation_result.py            │
│  - validation/validator.py              │  - compares results against reference data
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  domain                                 │  Core business logic (no dependencies)
│  - entities/engine.py                   │  - Engine, Nozzle (value objects)
│  - value_objects/operating_point.py     │  - OperatingPoint (value object)
│  - services/thrust_service.py           │  - computes thrust & Isp
│  - services/geometry_service.py         │  - computes nozzle geometry
│  - services/transient_service.py        │  - 0D chamber pressure transient
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  infrastructure                         │  External adapters (I/O concerns)
│  - cea/rocketcea_adapter.py           │  - RocketCEA thermochemistry wrapper
│  - config/engine_config_loader.py       │  - YAML parsing + Pydantic validation
│  - config/schema.py                     │  - EngineConfigSchema (Pydantic model)
│  - plotting/plotter.py                  │  - Plotly image generation
└─────────────────────────────────────────┘
```

**Dependency rule:** Inner layers never depend on outer layers. Domain has zero external dependencies. Application depends only on Domain. Infrastructure depends on Application DTOs. Interfaces depend on everything.

---

## Run Tests

Run the full test suite with coverage:

```powershell
pytest
```

Run linting and type checking:

```powershell
ruff check src/ tests/
mypy src/
```

---

## Project Status

- ✅ Domain models (Engine, Nozzle, OperatingPoint)
- ✅ Thrust & specific impulse calculation
- ✅ Nozzle geometry (L*, contraction ratio, bell nozzle)
- ✅ 0D chamber pressure transient
- ✅ RocketCEA integration for LOX/LH2 (and other propellants)
- ✅ YAML config validation with Pydantic
- ✅ Plotly plotting (PNG + HTML)
- ✅ Validation against reference data
- ✅ CI with GitHub Actions
- ✅ 99% test coverage

---

## License

MIT
